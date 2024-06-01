from . import ChatNVIDIA
from .nvdia_agent import NVDA_MODEL
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from .node import session_config, AgentState, StrategyStatus
import functools


ANALYST_SYSTEM_MESSAGE = """
You are a professional analyst who is responsible for analyzing the performance of a trading strategy.
Given the statistics of a trading strategy, you should provide a detailed analysis of the strategy's performance.
"""
DASHED_LINE = "\n----------------------------------------------\n"


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
    result = chain.invoke({
        "strategy_description": state["current_strategy"].description,
        "strategy_performance": state["current_strategy"].performance
        },
        config=session_config
    )
    result = AIMessage(**result.dict(exclude={"type", "name"}), name="Analyst")
    state["current_strategy"].status = StrategyStatus.DONE

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