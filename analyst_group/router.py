from .model import *
from .coding.code_executor import CodeResult
from .node import AgentState, StrategyStatus
from utils.fancy_log import FancyLogger

LOG = FancyLogger(__name__)


def qa_router(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    result = CodeResult.parse_obj(last_message.content[0])

    if StrategyStatus.HUMAN_SUPPORT in state["current_strategy"].status:
        return HUMAN_EDGE
    elif StrategyStatus.PENDING_DEBUGGING in state["current_strategy"].status:
        return DEBUGGING_EDGE
    elif StrategyStatus.PENDING_TUNING in state["current_strategy"].status:
        return CONTINUE_EDGE
    else:
        raise ValueError(f"No routing available for QA node: {result}")
        

def tuing_router(state:AgentState):
    if StrategyStatus.HUMAN_SUPPORT in state["current_strategy"].status:
        return HUMAN_EDGE
    if state["current_strategy"].status == StrategyStatus.PENDING_ANALYSIS:
        return CONTINUE_EDGE

    raise ValueError(f"Invalid state for tuning router: {state['current_strategy'].status}")


def human_router(state: AgentState):
    if StrategyStatus.PENDING_QA in state["current_strategy"].status:
        return QA_EDGE
    elif StrategyStatus.PENDING_TUNING in state["current_strategy"].status:
        return TUNING_EDGE

    raise ValueError(f"Invalid sender: {state['sender']}")


def analyst_router(state: AgentState):
    # TEMP: For now, human will check if the annual return is greater than 5.0
    res = input("Check if annaul return is greater than 5.0: ")
    if res == "y":
        return END_TASK_EDGE
    return CONTINUE_EDGE