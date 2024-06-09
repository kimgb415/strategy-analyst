from .backtest import run_backtest, analyze_strategy_result
from .base import PerformanceMetrics

TECH_GIANTS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

def calculate_average(metrics: list[PerformanceMetrics]) -> PerformanceMetrics:
    sharpe = sum(m.sharpe for m in metrics if m.sharpe is not None) / len([m for m in metrics if m.sharpe is not None])
    drawdown = sum(m.drawdown for m in metrics if m.drawdown is not None) / len([m for m in metrics if m.drawdown is not None])
    annual_return = sum(m.annual_return for m in metrics) / len(metrics)
    total_trades = sum(m.total_trades for m in metrics) / len(metrics)
    winning_trades = sum(m.winning_trades for m in metrics) / len(metrics)
    losing_trades = sum(m.losing_trades for m in metrics) / len(metrics)
    
    return PerformanceMetrics(
        sharpe=sharpe,
        drawdown=drawdown,
        annual_return=annual_return,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades
    )


if __name__ == "__main__":
    metrics = []
    for symbol in TECH_GIANTS:
        result = run_backtest(symbol, 2000)
        metrics.append(analyze_strategy_result(result))
    
    # construct average metrics
    avg_metric = calculate_average(metrics)


    print(avg_metric.json(indent=2))
