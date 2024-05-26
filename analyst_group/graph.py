from langgraph.graph import END, StateGraph
from .router import router
from .model import CONTINUE, TOOL_CALL
from .node import planning_node, AgentState, router_node


RESEARCH_NODE = "researcher"
RESEARCH_EXECUTOR_NODE = "research_executor"
PLANNER_NODE = "planner"
ROUTER_NODE = "router"


def create_analyst_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node(PLANNER_NODE, planning_node)
    workflow.add_node(ROUTER_NODE, router_node)
    
    workflow.add_edge(PLANNER_NODE, ROUTER_NODE)
    workflow.add_edge(ROUTER_NODE, END)


    workflow.set_entry_point(PLANNER_NODE)

    return workflow