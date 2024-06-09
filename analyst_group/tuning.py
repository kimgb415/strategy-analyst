from .base import DASHED_LINE
from langchain.prompts import ChatPromptTemplate
from .coding.code_extractor import PythonCodeExtractor
from .coding.code_executor import CodeExecutor, CodeResult
from .coding.code_saver import CodeSaver
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import os
from utils.fancy_log import FancyLogger
from .node import AgentState, StrategyStatus, session_config
import functools
from . import ChatNVIDIA, NVDA_MODEL
from .model import TUNING_SENDER


TUNING_SYSTEM_MESSAGE = """
You will be given a backtrader strategy implementaion.
Read the strategy code carefully and check the parameters that should be tuned.
Provide the definition of `params_to_optimize` and wrap it in python code block. 
Try not to provide permutations of the parameters more than 1000.
"""
EXAMPLE_PARAMS_OUTPUT = """
```python
params_to_optimize = dict(
    ema_period=range(10, 51, 5),
    sma_period=range(1, 4),
    atr_period=range(5, 21, 2),
    atr_threshold=(1.0, 2.0, 0.5),
)
```
"""
LOG = FancyLogger(__name__)


def create_tuing_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                TUNING_SYSTEM_MESSAGE
            ),
            (
                "user",
                f"{DASHED_LINE}"
                "STRATEGY CODE: \n```python\n{strategy_code}```"
                f"{DASHED_LINE}"
                f"EXAMPLE PARAMS OUTPUT: \n{EXAMPLE_PARAMS_OUTPUT}"
            ),
        ]
    )
    extractor = RunnableLambda(PythonCodeExtractor())
    saver = RunnableLambda(CodeSaver(os.path.join('backtesting', 'params.py')))

    return prompt | llm | StrOutputParser() | extractor | saver


def process_tuning_node(state: AgentState, llm) -> AgentState:
    invoke_input = {
        "strategy_code": state["current_strategy"].code,
    },

    LOG.info(f"Generating params for strategy optimization")
    chain = create_tuing_chain(llm)
    param_output = chain.invoke(invoke_input, config=session_config)
    state["current_strategy"].params = param_output

    LOG.info(f"Optimizing strategy with params:\n{param_output}")
    executor = RunnableLambda(CodeExecutor('backtesting', args='--opt'))
    result = executor.invoke({}, config=session_config)

    code_result = CodeResult.parse_obj(result.content[0])
    if code_result.exit_code == 0:
        state["current_strategy"].status = StrategyStatus.PENDING_ANALYSIS
        state["current_strategy"].performance = code_result.output
        LOG.info(f"Tuning complete with best result\n{code_result.output}")
    else:
        LOG.error(f"Error processing tuning node: {code_result.output}")
        state["current_strategy"].status |= StrategyStatus.HUMAN_SUPPORT
    
    return AgentState(
        messages=[result],
        sender=TUNING_SENDER,
        current_strategy=state["current_strategy"],
        debugging_count=state["debugging_count"]
    )


tuning_node = functools.partial(process_tuning_node, llm=ChatNVIDIA(model=NVDA_MODEL))