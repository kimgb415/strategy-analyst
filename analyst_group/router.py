from langgraph.graph import END
from .model import TOOL_CALL, END_TASK, CONTINUE
from .coding.code_executor import ExecutorMessage


def qa_router(state):
    messages = state["messages"]

    last_message : ExecutorMessage = messages[-1]
    
    if not isinstance(last_message, ExecutorMessage):
        raise ValueError("The last message sent to QA router is not an ExecutorMessage")
    
    return
    

def router(state):
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if TOOL_CALL in last_message.content:
        return TOOL_CALL
    if END_TASK in last_message.content:
        # Any agent decided the work is done
        return END
    return CONTINUE