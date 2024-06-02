from analyst_group.graph import create_analyst_workflow
from IPython.display import display, Image
from langchain_core.messages import HumanMessage
from pprint import pformat
from utils.fancy_log import FancyLogger
import os

LOG = FancyLogger(__name__)


if not os.getenv("NVIDIA_API_KEY", None):
    raise ValueError("NVIDIA_API_KEY is not set in the environment variables.")

workflow = create_analyst_workflow()
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
    {"recursion_limit": 13},
)


for s in events:
    # LOG.info(pformat(s))
    LOG.info("----------------------")