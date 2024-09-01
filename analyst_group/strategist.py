from . import ChatModel, CHAT_MODEL_NAME
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .node import AgentState, session_config, TradingStrategy, StrategyStatus
from langchain_core.messages import AIMessage
import functools
from enum import Enum
from utils.fancy_log import FancyLogger
from .model import STRATEGIST_SENDER

LOG = FancyLogger(__name__)
STRATEGIST_SYSTEM_MESSAGE = """
You are a professional trader relying ONLY on technical & quantitative analysis of the target company.
You don't overthink the company's fundamentals, you just focus on the numbers.
Don't provide any information that is not related to the description of strategy.
"""

class StrategistTask(Enum):
    IMPLEMENT_STRATEGY = "IMPLEMENT_STRATEGY"
    IMPROVE_STRATEGY = "IMPROVE_STRATEGY"


def get_strategist_prompt(task: StrategistTask):
    if task == StrategistTask.IMPLEMENT_STRATEGY:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    STRATEGIST_SYSTEM_MESSAGE
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
    elif task == StrategistTask.IMPROVE_STRATEGY:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    STRATEGIST_SYSTEM_MESSAGE
                ),
                (
                    "user",
                    "Based on the critique, improve the original strategy."
                    "\n----------------------------------------------\n"
                    "ORIGINAL STRATEGY DESCRIPTION: \n{strategy_description}"
                    "\n----------------------------------------------\n"
                    "CRITIQUE: \n{strategy_critique}"
                )
            ]
        )    
    

    return prompt


def process_strategist_node(state: AgentState, llm):
    if state["current_strategy"] is None:
        prompt = get_strategist_prompt(StrategistTask.IMPLEMENT_STRATEGY)
        invoke_input = state
        LOG.info("Describing a new strategy")
    elif state["current_strategy"].status == StrategyStatus.PENDING_IMPROVEMENT:
        prompt = get_strategist_prompt(StrategistTask.IMPROVE_STRATEGY)
        last_message = state["messages"][-1]
        invoke_input = {
                "strategy_description": state["current_strategy"].description, 
                "strategy_critique": last_message.content
        }
        LOG.info("Improving the strategy")
    
    chain = prompt | llm
    chain_response = chain.invoke(invoke_input, config=session_config)

    new_strategy = TradingStrategy(
        description=chain_response.content, 
        status=StrategyStatus.PENDING_IMPELEMENTATION
    )
    chain_response = AIMessage(**chain_response.dict(exclude={"type", "name"}), name="Strategist")
    

    return AgentState(
        messages=[chain_response],
        sender=STRATEGIST_SENDER,
        current_strategy=new_strategy,
        debugging_count=state["debugging_count"]
    )


strategist_node = functools.partial(
    process_strategist_node, 
    llm=ChatModel(model_name=CHAT_MODEL_NAME)
)