from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, Union


class PerformanceMetrics(BaseModel):
    sharpe: Optional[float] = Field(None, description="Sharpe Ratio")
    drawdown: Optional[float] = Field(None, description="Maximum Drawdown")
    annual_return: float = Field(..., description="Annual Return")
    total_trades: Union[int, float] = Field(..., description="Total Trades")
    winning_trades: Union[int, float] = Field(..., description="Winning Trades")
    losing_trades: Union[int, float] = Field(..., description="Losing Trades")
