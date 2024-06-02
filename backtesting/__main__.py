from .backtest import run_backtest, analyze_strategy_result


if __name__ == "__main__":
    result = run_backtest('AAPL', 1990)
    metric = analyze_strategy_result(result)

    print(metric.json(indent=2))
