from langgraph.graph import END, StateGraph
from .router import router
from .model import CONTINUE, TOOL_CALL
from .node import AgentState
from .coder import coding_node, QA_node


RESEARCH_NODE = "researcher"
RESEARCH_EXECUTOR_NODE = "research_executor"
PLANNER_NODE = "planner"
ROUTER_NODE = "router"
CODER_NODE = "coder"
QA_NODE = 'QA'


def create_analyst_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node(CODER_NODE, coding_node)
    workflow.add_node(QA_NODE, QA_node)
    
    workflow.add_edge(CODER_NODE, QA_NODE)
    workflow.add_edge(QA_NODE, END)

    workflow.set_entry_point(CODER_NODE)

    return workflow