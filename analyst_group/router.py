from .model import CONTINUE_EDGE, DEBUGGING_EDGE, FORCE_END_EDGE
from .coding.code_executor import ExecutorMessage
from .node import AgentState

MAX_DEBUGGING_COUNT = 5

def qa_router(state: AgentState):
    messages = state["messages"]

    last_message : ExecutorMessage = messages[-1]
    
    if not isinstance(last_message, ExecutorMessage):
        raise ValueError("The last message sent to QA router is not an ExecutorMessage")
    
    if last_message.result.exit_code == 0:
        return CONTINUE_EDGE
    else:
        return DEBUGGING_EDGE
    
def debugging_router(state: AgentState):
    if state["debugging_count"] < MAX_DEBUGGING_COUNT:
        return CONTINUE_EDGE
    return FORCE_END_EDGE