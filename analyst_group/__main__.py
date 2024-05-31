from analyst_group.graph import create_analyst_workflow
from IPython.display import display, Image
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from pprint import pformat
from utils.fancy_log import FancyLogger

LOG = FancyLogger(__name__)

load_dotenv()

workflow = create_analyst_workflow()
graph = workflow.compile()

events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Implement a backtrader strategy class named 'MyStrategy' using indicators and signals."
                "Do not include the backtesting code. Just provide the strategy class."
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 5},
)


for s in events:
    LOG.info(pformat(s))
    LOG.info("----------------------")