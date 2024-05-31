from . import ChatNVIDIA
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .nvdia_agent import NVDA_MODEL
from .coding.code_extractor import PythonCodeExtractor
from .coding.code_saver import CodeSaver
from .coding.code_executor import CodeExecutor
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
import os
from .history import get_sql_session_id
from .node import agent_node, agent_state_parser
import functools


CODER_SYSTEM_MESSAGE_SIDE_NOTES = """Wrap your code in a code block that specifies the script type. 
    The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
    Don't use a code block if it's not intended to be executed by the executor. Don't include multiple code blocks in one response. 
    Suggest the full code instead of partial code or code changes, including the original code. 
"""
# The key for the messages in the AgentState
AGENT_STATE_MESSAGE_KEY='messages'


def create_coding_agnet(llm: ChatNVIDIA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                CODER_SYSTEM_MESSAGE_SIDE_NOTES
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm


def create_coding_agent_with_history(chain):
    return RunnableWithMessageHistory(
        chain,
        get_session_history=get_sql_session_id,
        input_messages_key=AGENT_STATE_MESSAGE_KEY,
    )


def create_quality_assurance_chain():
    state_parser = RunnableLambda(agent_state_parser)
    extractor = RunnableLambda(PythonCodeExtractor())
    saver = RunnableLambda(CodeSaver(os.path.join('backtesting', 'strategy.py')))
    executor = RunnableLambda(CodeExecutor('backtesting'))

    return  state_parser | extractor | saver | executor


def create_quality_assurance_chain_with_history(chain):
    return RunnableWithMessageHistory(
        chain,
        get_session_history=get_sql_session_id,
        input_messages_key=AGENT_STATE_MESSAGE_KEY,
    )


coding_chain = create_coding_agent_with_history(
    create_coding_agnet(ChatNVIDIA(model=NVDA_MODEL))
)
QA_chain = create_quality_assurance_chain_with_history(
    create_quality_assurance_chain()
)
coding_node = functools.partial(agent_node, agent=coding_chain, name="coder")
QA_node = functools.partial(agent_node, agent=QA_chain, name="QA")