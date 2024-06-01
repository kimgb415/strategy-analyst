from . import ChatNVIDIA
from langchain.prompts import ChatPromptTemplate
from .nvdia_agent import NVDA_MODEL
from .coding.code_extractor import PythonCodeExtractor
from .coding.code_saver import CodeSaver
from .coding.code_executor import CodeExecutor, ExecutorMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
import os
from .node import StrategyStatus, AgentState, session_config
import functools
from enum import Enum


CODER_SYSTEM_MESSAGE_SIDE_NOTES = """Wrap your code in a code block that specifies the script type. 
    The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
    Don't use a code block if it's not intended to be executed by the executor. Don't include multiple code blocks in one response. 
    Suggest the full code instead of partial code or code changes, including the original code. 
"""

class CodingTask(Enum):
    IMPLEMENT_STRATEGY = "IMPLEMENT_STRATEGY"
    DEBUG_STRATEGY = "DEBUG_STRATEGY"


def create_coding_chain(llm, task: CodingTask):
    if task == CodingTask.IMPLEMENT_STRATEGY:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    CODER_SYSTEM_MESSAGE_SIDE_NOTES
                ),
                (
                    'user',
                    "Implement a python backtrader strategy class named 'MyStrategy' based on following description of the target strategy."
                    "Do not include the backtesting code. Just provide the strategy class."
                    "----------------------------------------------"
                    "STRATEGY DESCRIPTION: \n{strategy_description}"
                )
            ]
        )
    elif task == CodingTask.DEBUG_STRATEGY:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    CODER_SYSTEM_MESSAGE_SIDE_NOTES
                ),
                (
                    "user",
                    "You are a professional problem solver, debug the following code and provide the corrected one."
                    "You should focus on traceback and error messages to identify the issue."
                    "----------------------------------------------"
                    "PROBLEMATIC CODE:\n{code}"
                    "----------------------------------------------"
                    "EXECUTION RESULT:\n{outptus}"
                )
            ]
        )   
    

    extractor = RunnableLambda(PythonCodeExtractor())
    saver = RunnableLambda(CodeSaver(os.path.join('backtesting', 'strategy.py')))

    return prompt | llm | StrOutputParser() | extractor | saver


def process_coding_node(state: AgentState, chain, task: CodingTask) -> AgentState:
    if task == CodingTask.IMPLEMENT_STRATEGY:
        result = chain.invoke(
            {"strategy_description": state["current_strategy"].description},
            config=session_config
        )
    elif task == CodingTask.DEBUG_STRATEGY:
        last_message : ExecutorMessage = state["messages"][-1]
        result = chain.invoke(
            {"code": state["current_strategy"].code, "outptus": last_message.result.output},
            config=session_config
        )    


    # udpate current strategy
    state["current_strategy"].code = result
    state["current_strategy"].status = StrategyStatus.PENDING_QA
    

    return AgentState(
        messages=[AIMessage(content=result, name="coder")],
        sender="coder",
        current_strategy=state["current_strategy"]
    )


def create_QA_chain():
    executor = RunnableLambda(CodeExecutor('backtesting'))

    return executor


def process_QA_node(state: AgentState, chain) -> AgentState:
    result : ExecutorMessage = chain.invoke(state, config=session_config)
    
    if result.result.exit_code == 0:
        state["current_strategy"].status = StrategyStatus.PENDING_ANALYSIS
    else:
        state["current_strategy"].status = StrategyStatus.PENDING_DEBUGGING

    return AgentState(
        messages=[result],
        sender="QA",
        current_strategy=state["current_strategy"]
    )


coding_node = functools.partial(
    process_coding_node, 
    chain=create_coding_chain(
        ChatNVIDIA(model=NVDA_MODEL),
        CodingTask.IMPLEMENT_STRATEGY
    ),
    task=CodingTask.IMPLEMENT_STRATEGY
)

QA_node = functools.partial(
    process_QA_node,
    chain=create_QA_chain(),
)

debugging_node = functools.partial(
    process_coding_node,
    chain=create_coding_chain(
        ChatNVIDIA(model=NVDA_MODEL),
        CodingTask.DEBUG_STRATEGY
    ),
    task=CodingTask.DEBUG_STRATEGY
)