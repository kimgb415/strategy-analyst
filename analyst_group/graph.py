from langgraph.graph import END, StateGraph
from .router import qa_router, analyst_router
from .model import CONTINUE_EDGE, DEBUGGING_EDGE, FORCE_END_EDGE, END_TASK_EDGE
from .node import AgentState
from .coder import coding_node, QA_node
from .strategist import strategist_node
from .analyst import analyst_node


CODER_NODE = "coder"
QA_NODE = 'QA'
STRATEGY_NODE = 'strategy'
DEBUGGING_NODE = 'debugging'
ANALYST_NODE = 'analyst'


def create_analyst_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node(STRATEGY_NODE, strategist_node)
    workflow.add_node(CODER_NODE, coding_node)
    workflow.add_node(QA_NODE, QA_node)
    workflow.add_node(ANALYST_NODE, analyst_node)

    workflow.add_edge(STRATEGY_NODE, CODER_NODE)
    workflow.add_edge(CODER_NODE, QA_NODE)
    workflow.add_conditional_edges(
        QA_NODE,
        qa_router,
        {
            CONTINUE_EDGE: ANALYST_NODE,
            DEBUGGING_EDGE: CODER_NODE,
            FORCE_END_EDGE: END
        }
    )
    workflow.add_conditional_edges(
        ANALYST_NODE,
        analyst_router,
        {
            CONTINUE_EDGE: STRATEGY_NODE,
            END_TASK_EDGE: END
        }
    )


    workflow.set_entry_point(STRATEGY_NODE)

    return workflow