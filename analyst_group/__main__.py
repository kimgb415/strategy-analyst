from analyst_group.graph import create_analyst_workflow
from IPython.display import display, Image
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

workflow = create_analyst_workflow()
graph = workflow.compile()

events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Implement a backtrader strategy class named 'MyStrategy' using indicators and signals."
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 5},
)


for s in events:
    pprint(s.items())
    # print(s)
    # print("----")
    pass