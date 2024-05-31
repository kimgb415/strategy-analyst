from langchain_core.messages import AIMessage, ToolMessage
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
import operator


session_config = {"configurable": {"session_id": "dev"}}


class AgentState(TypedDict):
    # NOTE: Reducers provided as annotations tell the graph how to process updates for this field.
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


def agent_state_parser(state: AgentState) -> str:
    return state['messages'][-1]


# Helper function to create a node for a given agent
def agent_node(state: AgentState, agent, name) -> AgentState:
    result = agent.invoke(state, config=session_config)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    elif hasattr(result, 'dict'):
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)


    return AgentState(
        messages=[result],
        sender=name,
    )

