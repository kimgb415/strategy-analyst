from . import ChatModel, CHAT_MODEL_NAME
from langchain.prompts import ChatPromptTemplate
from .coding.code_extractor import PythonCodeExtractor
from .coding.code_saver import CodeSaver
from .coding.code_executor import CodeExecutor, CodeResult
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
import os
from .node import StrategyStatus, AgentState, session_config
import functools
from enum import Enum
from utils.fancy_log import FancyLogger
from .base import DASHED_LINE
from .model import CODER_SENDER, QA_SENDER, HUMAN_SENDER

LOG = FancyLogger(__name__)
MAX_DEBUGGING_COUNT = 5


CODER_SYSTEM_MESSAGE = """Wrap your code in a code block that specifies the script type. 
    The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
    Don't use a code block if it's not intended to be executed by the executor. Don't include multiple code blocks in one response. 
    Don't include print or logging statements in the code block.
    Suggest the full code instead of partial code or code changes, including the original code. 
"""


class CodingTask(Enum):
    IMPLEMENT_STRATEGY = "IMPLEMENT_STRATEGY"
    DEBUG_STRATEGY = "DEBUG_STRATEGY"


def get_coding_prompt(task: CodingTask):
    if task == CodingTask.IMPLEMENT_STRATEGY:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'user',
                    f"{CODER_SYSTEM_MESSAGE}"
                    "Implement a python backtrader strategy class named 'MyStrategy' based on following description of the target strategy."
                    "Do not include the backtesting code. Just provide the strategy class."
                    f"{DASHED_LINE}"
                    "STRATEGY DESCRIPTION: \n{strategy_description}"
                )
            ]
        )
    elif task == CodingTask.DEBUG_STRATEGY:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "user",
                    f"{CODER_SYSTEM_MESSAGE}"
                    "You are currenlty implementing a trading strategy. Based on the output of the backtesting code, "
                    "provide the corrected code that is error free and sticks to the original strategy description."
                    "NOTE: If division by zero error occurs, set safediv=True for the initialization of RSI realted indicator."
                    f"{DASHED_LINE}"
                    "STRATEGY DESCRIPTION: \n{strategy_description}"
                    f"{DASHED_LINE}"
                    "PROBLEMATIC CODE:\n{code}"
                    f"{DASHED_LINE}"
                    "EXECUTION RESULT:\n{outptus}"
                )
            ]
        )

    return prompt


def create_coding_chain(llm):
    extractor = RunnableLambda(PythonCodeExtractor())
    saver = RunnableLambda(CodeSaver(os.path.join('backtesting', 'strategy.py')))

    return llm | StrOutputParser() | extractor | saver


def process_coding_node(state: AgentState, llm) -> AgentState:
    if state["current_strategy"].status == StrategyStatus.PENDING_IMPELEMENTATION:
        prompt = get_coding_prompt(CodingTask.IMPLEMENT_STRATEGY)
        invoke_input = {"strategy_description": state["current_strategy"].description},
        # reset debugging count
        state["debugging_count"] = 0
        LOG.info("Coding task: Implementing strategy")
    elif state["current_strategy"].status == StrategyStatus.PENDING_DEBUGGING:
        prompt = get_coding_prompt(CodingTask.DEBUG_STRATEGY)
        code_result = CodeResult.parse_obj(state["messages"][-1].content[0])
        invoke_input = {
            "strategy_description": state["current_strategy"].description,
            "code": state["current_strategy"].code,
            "outptus": code_result.output,
        }
        # increment debugging count
        state["debugging_count"] += 1
        LOG.info(f"Coding task: Debugging strategy: {state['debugging_count']}th attempt") 

    chain = prompt | create_coding_chain(llm)
    # NOTE: There are times when the code is not properly warpped by LLM
    try:
        result = chain.invoke(invoke_input, config=session_config)

        # udpate current strategy
        state["current_strategy"].code = result
        state["current_strategy"].status = StrategyStatus.PENDING_QA
    except Exception as e:
        LOG.error(f"Error processing coding node: {e}")
        result = f"Error processing coding node: {e}"
        state["current_strategy"].status |= StrategyStatus.HUMAN_SUPPORT

    return AgentState(
        messages=[AIMessage(content=result, name="coder")],
        sender=CODER_SENDER,
        current_strategy=state["current_strategy"],
        debugging_count=state["debugging_count"]
    )


def create_QA_chain():
    executor = RunnableLambda(CodeExecutor('backtesting'))

    return executor


def process_QA_node(state: AgentState, chain) -> AgentState:
    result = chain.invoke(state, config=session_config)
    code_result = CodeResult.parse_obj(result.content[0])
    
    if state["sender"] == HUMAN_SENDER:
        LOG.debug("Returned from human support. Resetting flags and debugging count.")
        state["current_strategy"].status &= ~StrategyStatus.HUMAN_SUPPORT
        state["debugging_count"] = 0

    if code_result.exit_code == 0:
        state["current_strategy"].status = StrategyStatus.PENDING_TUNING
        LOG.info(f"QA passed with output: {code_result.output}")
    else:
        LOG.debug(f"QA failed with output: {code_result.output}")
        state["current_strategy"].status = StrategyStatus.PENDING_DEBUGGING
        if state["debugging_count"] >= MAX_DEBUGGING_COUNT:
            LOG.warning("Debugging count exceeded. Requesting human support")
            state["current_strategy"].status |= StrategyStatus.HUMAN_SUPPORT

    return AgentState(
        messages=[result],
        sender=QA_SENDER,
        current_strategy=state["current_strategy"],
        debugging_count=state["debugging_count"]
    )


coding_node = functools.partial(
    process_coding_node, 
    llm=ChatModel(model=CHAT_MODEL_NAME)
)

QA_node = functools.partial(
    process_QA_node,
    chain=create_QA_chain(),
)