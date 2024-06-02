from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional


class PerformanceMetrics(BaseModel):
    sharpe: Optional[float] = Field(None, description="Sharpe Ratio")
    drawdown: Optional[float] = Field(None, description="Maximum Drawdown")
    annual_return: float = Field(..., description="Annual Return")
    total_trades: int = Field(..., description="Total Trades")
    winning_trades: int = Field(..., description="Winning Trades")
    losing_trades: int = Field(..., description="Losing Trades")
