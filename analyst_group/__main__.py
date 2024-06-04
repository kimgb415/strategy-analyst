from analyst_group.graph import create_analyst_workflow
from IPython.display import display, Image
from langchain_core.messages import HumanMessage
from pprint import pformat
from utils.fancy_log import FancyLogger
from langgraph.checkpoint.sqlite import SqliteSaver
import os

LOG = FancyLogger(__name__)


if not os.getenv("NVIDIA_API_KEY", None):
    raise ValueError("NVIDIA_API_KEY is not set in the environment variables.")

memory = SqliteSaver.from_conn_string("graph.db")
workflow = create_analyst_workflow()
# graph = workflow.compile(checkpointer=memory)
graph = workflow.compile()

events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Describe a quantitative trading strategy that is consice and simple."
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 50},
)


for s in events:
    # LOG.info(pformat(s))
    LOG.info("----------------------")