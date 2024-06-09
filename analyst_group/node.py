from typing import Annotated, Sequence, TypedDict, Union
from langchain_core.messages import BaseMessage
import operator
from langchain_core.pydantic_v1 import BaseModel, Field
from backtesting import PerformanceMetrics
from enum import Flag, auto


# The key for the messages in the AgentState
AGENT_STATE_MESSAGE_KEY='messages'

session_config = {"configurable": {"session_id": "dev"}}


class StrategyStatus(Flag):
    PENDING_IMPELEMENTATION = auto()
    PENDING_QA = auto()
    PENDING_TUNING = auto()
    PENDING_ANALYSIS = auto()
    PENDING_DEBUGGING = auto()
    PENDING_IMPROVEMENT = auto()
    HUMAN_SUPPORT = auto()
    DONE = auto()


class TradingStrategy(BaseModel):
    description: str = Field(..., description="Description of the strategy")
    code: str = Field(default=None, description="Python code of the strategy")
    performance: str = Field(default=None, description="Performance of the strategy after backtesting")
    status : StrategyStatus = StrategyStatus.PENDING_IMPELEMENTATION
    params: str = Field(default=None, description="Param dictionary for strategy optimization")


class AgentState(TypedDict):
    # NOTE: Reducers provided as annotations tell the graph how to process updates for this field.
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    current_strategy: TradingStrategy = None
    debugging_count: int = 0