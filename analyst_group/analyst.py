from . import ChatNVIDIA, NVDA_MODEL
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from .node import session_config, AgentState, StrategyStatus
import functools
from utils.fancy_log import FancyLogger
from datetime import datetime
import os
from pprint import pformat

LOG = FancyLogger(__name__)
ANALYST_SYSTEM_MESSAGE = """
You are a professional analyst who is responsible for analyzing the performance of a trading strategy.
Given the statistics of a trading strategy, you should provide a detailed analysis of the strategy's performance.
"""
DASHED_LINE = "\n----------------------------------------------\n"

def generate_analysis_report(state: AgentState, analysis: str):
    report = f"""# Strategy Description:
{state["current_strategy"].description}

# Strategy Performance:
{pformat(state["current_strategy"].performance)}

# Analysis:
{analysis}

# Strategy Code:
```python
{state['current_strategy'].code}
```
"""
    
    report_file_name = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_strategy.md'
    os.makedirs('report', exist_ok=True)
    with open(os.path.join('report', report_file_name), 'w') as file:
        file.write(report)


def create_analyst_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                ANALYST_SYSTEM_MESSAGE
            ),
            (
                "user",
                f"{DASHED_LINE}"
                "STRATEGY DESCRIPTION: \n{strategy_description}"
                f"{DASHED_LINE}"
                "STRATEGY STATISTICS: \n{strategy_performance}"
            ),
        ]
    )

    return prompt | llm


def process_analyst_node(state: AgentState, chain) -> AgentState:
    LOG.info("Analyzing backtesting performance")
    result = chain.invoke({
        "strategy_description": state["current_strategy"].description,
        "strategy_performance": state["current_strategy"].performance
        },
        config=session_config
    )
    generate_analysis_report(state, result.content)

    result = AIMessage(**result.dict(exclude={"type", "name"}), name="Analyst")
    state["current_strategy"].status = StrategyStatus.PENDING_IMPROVEMENT

    input("Press Enter to continue...")

    return AgentState(
        messages=[result],
        sender="Analyst",
        current_strategy=state["current_strategy"],
        debugging_count=state["debugging_count"]
   )

analyst_node = functools.partial(
    process_analyst_node,
    chain=create_analyst_chain(ChatNVIDIA(model=NVDA_MODEL))
)