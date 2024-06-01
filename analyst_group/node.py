from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
import operator
from langchain_core.pydantic_v1 import BaseModel, Field
from enum import Enum


# The key for the messages in the AgentState
AGENT_STATE_MESSAGE_KEY='messages'

session_config = {"configurable": {"session_id": "dev"}}


class StrategyStatus(Enum):
    PENDING_IMPELEMENTATION = "PENDING_IMPLEMENTATION"
    PENDING_QA = "PENDING_QA"
    PENDING_ANALYSIS = "PENDING_ANALYSIS"
    PENDING_DEBUGGING = "PENDING_DEBUGGING"
    DONE = "DONE"


class TradingStrategy(BaseModel):
    description: str = Field(..., description="Description of the strategy")
    code: str = Field(default=None, description="Python code of the strategy")
    performance: str = Field(default=None, description="Performance of the strategy after backtesting")
    status : StrategyStatus = StrategyStatus.PENDING_IMPELEMENTATION


class AgentState(TypedDict):
    # NOTE: Reducers provided as annotations tell the graph how to process updates for this field.
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    current_strategy: TradingStrategy = None
    debugging_count: int = 0