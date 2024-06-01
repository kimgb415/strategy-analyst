from langgraph.graph import END, StateGraph
from .router import qa_router
from .model import CONTINUE_EDGE, DEBUGGING_EDGE
from .node import AgentState
from .coder import coding_node, QA_node, debugging_node
from .strategist import strategist_node

RESEARCH_NODE = "researcher"
RESEARCH_EXECUTOR_NODE = "research_executor"
PLANNER_NODE = "planner"
ROUTER_NODE = "router"
CODER_NODE = "coder"
QA_NODE = 'QA'
STRATEGY_NODE = 'strategy'
DEBUGGING_NODE = 'debugging'


def create_analyst_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node(STRATEGY_NODE, strategist_node)
    workflow.add_node(CODER_NODE, coding_node)
    workflow.add_node(QA_NODE, QA_node)
    workflow.add_node(DEBUGGING_NODE, debugging_node)

    workflow.add_edge(STRATEGY_NODE, CODER_NODE)
    workflow.add_edge(CODER_NODE, QA_NODE)
    workflow.add_conditional_edges(
        QA_NODE,
        qa_router,
        {CONTINUE_EDGE: END, DEBUGGING_EDGE: DEBUGGING_NODE}
    )
    workflow.add_edge(DEBUGGING_NODE, END)


    workflow.set_entry_point(STRATEGY_NODE)

    return workflow