from . import ChatNVIDIA
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .nvdia_agent import NVDA_MODEL
from .node import AgentState, session_config, TradingStrategy, StrategyStatus, AGENT_STATE_MESSAGE_KEY
from langchain_core.messages import AIMessage
import functools


STRATEGIST_SYSTEM_MESSAGE = """
You are a professional trader relying ONLY on technical & quantitative analysis of the target company.
You don't overthink the company's fundamentals, you just focus on the numbers.
"""


def create_strategist_chain(llm: ChatNVIDIA):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                STRATEGIST_SYSTEM_MESSAGE
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt | llm


def process_strategist_node(state: AgentState, chain):
    result = chain.invoke(state, config=session_config)
    new_strategy = TradingStrategy(
        description=result.content, 
        status=StrategyStatus.PENDING_IMPELEMENTATION
    )
    result = AIMessage(**result.dict(exclude={"type", "name"}), name="Strategist")
    

    return AgentState(
        messages=[result],
        sender="Strategist",
        current_strategy=new_strategy
    )


strategist_node = functools.partial(
    process_strategist_node, 
    chain=create_strategist_chain(ChatNVIDIA(model=NVDA_MODEL))
)