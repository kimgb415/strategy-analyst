from langchain_core.messages import AIMessage, ToolMessage
from .planner import planning_agent
from .coder import coding_agent
from .nvdia_agent import router_agent
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
import operator
import functools
from pprint import pprint


class AgentState(TypedDict):
    # NOTE: Reducers provided as annotations tell the graph how to process updates for this field.
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


# Helper function to create a node for a given agent
def agent_node(state: AgentState, agent, name) -> AgentState:
    result = agent.invoke(state)
    pprint(result)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    elif hasattr(result, 'dict'):
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)


    return AgentState(
        messages=[result],
        sender=name,
    )


planning_node = functools.partial(agent_node, agent=planning_agent, name="planner")
coding_node = functools.partial(agent_node, agent=coding_agent, name="coder")
router_node = functools.partial(agent_node, agent=router_agent, name="router")