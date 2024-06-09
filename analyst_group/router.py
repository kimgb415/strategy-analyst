from .model import CONTINUE_EDGE, DEBUGGING_EDGE, FORCE_END_EDGE, END_TASK_EDGE, HUMAN_EDGE
from .coding.code_executor import CodeResult
from .node import AgentState, StrategyStatus


MAX_DEBUGGING_COUNT = 5


def qa_router(state: AgentState):
    messages = state["messages"]

    last_message = messages[-1]
    try:
        result = CodeResult.parse_obj(last_message.content[0])
        if state["current_strategy"].status == StrategyStatus.HUMAN_SUPPORT:
            return HUMAN_EDGE
        elif result.exit_code == 0:
            return CONTINUE_EDGE
        elif state["debugging_count"] < MAX_DEBUGGING_COUNT:
            return DEBUGGING_EDGE
        else:
            state["debugging_count"] = 0
            return HUMAN_EDGE
    except Exception as e:
        raise ValueError(f"The last message sent to QA router is not valid: {e}")


def analyst_router(state: AgentState):
    if state["current_strategy"].performance.annual_return > 5.0:
        return END_TASK_EDGE
    return CONTINUE_EDGE