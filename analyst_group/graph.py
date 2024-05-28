from langgraph.graph import END, StateGraph
from .router import router
from .model import CONTINUE, TOOL_CALL
from .node import planning_node, AgentState, coding_node


RESEARCH_NODE = "researcher"
RESEARCH_EXECUTOR_NODE = "research_executor"
PLANNER_NODE = "planner"
ROUTER_NODE = "router"
CODER_NODE = "coder"


def create_analyst_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node(PLANNER_NODE, planning_node)
    workflow.add_node(CODER_NODE, coding_node)
    
    workflow.add_edge(PLANNER_NODE, CODER_NODE)
    workflow.add_edge(CODER_NODE, END)

    workflow.set_entry_point(PLANNER_NODE)

    return workflow