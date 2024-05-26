from langchain_core.messages import AIMessage, ToolMessage
from .nvdia_agent import planning_agent, router_agent
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
import operator
import functools


class AgentState(TypedDict):
    # NOTE: Reducers provided as annotations tell the graph how to process updates for this field.
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


# Helper function to create a node for a given agent
def agent_node(state: AgentState, agent, name) -> AgentState:
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)


    return AgentState(
        messages=[result],
        sender=name,
    )


planning_node = functools.partial(agent_node, agent=planning_agent, name="planner")
router_node = functools.partial(agent_node, agent=router_agent, name="router")