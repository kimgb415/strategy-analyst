from .backtest import (
    run_backtest, 
    analyze_strategy_result,
    run_backtest_optimization
)
import argparse
from .base import PerformanceMetrics

SYMBOL = "AAPL"
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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa", action='store_true', help="Test the strategy with the given symbol")
    parser.add_argument("--opt", action='store_true', help="Run optimization for the strategy")
    parser.add_argument("--avg", action='store_true', help="Compute the average perfromance the strategy with other tech giants")

    return parser.parse_args()


def main():
    args = get_args()
    if args.qa:
        result = run_backtest(SYMBOL, 2000)
        metric = analyze_strategy_result(result)
        print(metric.json(indent=2))
    elif args.opt:
        opt_df = run_backtest_optimization(SYMBOL, 2000)
        opt_df.sort_values('annual_return', ascending=False, inplace=True)
        print(opt_df.iloc[0])
    elif args.avg:
        metrics = []
        for symbol in TECH_GIANTS:
            result = run_backtest(symbol, 2000)
            metrics.append(analyze_strategy_result(result))
            print(f"Metrics for {symbol}")
            print(metrics[-1].json(indent=2))
        
        avg_metric = calculate_average(metrics)
        print(avg_metric.json(indent=2))


if __name__ == "__main__":
    main()