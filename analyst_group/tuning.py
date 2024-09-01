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
from . import ChatModel, CHAT_MODEL_NAME
from .model import TUNING_SENDER, QA_SENDER, HUMAN_SENDER


TUNING_SYSTEM_MESSAGE = """
You will be given a backtrader strategy implementaion.
Read the strategy code carefully and check the parameters that should be tuned.
You should only provide upto 6 parameters to optimize, with each parameter having upto 4 permutations.
Provide the definition of `params_to_optimize` and wrap it in python code block. 
"""
EXAMPLE_PARAMS_OUTPUT = """
```python
params_to_optimize = dict(
    ema_period=(10, 20, 30, 40),
    sma_period=(1, 4, 10, 15),
    atr_period=(5, 12, 21),
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
    if state["sender"] == QA_SENDER:
        invoke_input = {
            "strategy_code": state["current_strategy"].code,
        },

        LOG.info(f"Generating params for strategy optimization")
        chain = create_tuing_chain(llm)
        param_output = chain.invoke(invoke_input, config=session_config)
        state["current_strategy"].params = param_output
    elif state["sender"] == HUMAN_SENDER:
        # clear human support flag
        state["current_strategy"].status &= ~StrategyStatus.HUMAN_SUPPORT
    else:
        raise ValueError(f"Invalid sender to tuning edge: {state['sender']}")

    LOG.info(f"Optimizing strategy with params:\n{state['current_strategy'].params}")
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


tuning_node = functools.partial(process_tuning_node, llm=ChatModel(model=CHAT_MODEL_NAME))