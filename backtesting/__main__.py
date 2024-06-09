from .backtest import (
    run_backtest, 
    analyze_strategy_result,
    run_backtest_optimization
)
import argparse

SYMBOL = "AAPL"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa", action='store_true', help="Test the strategy with the given symbol")
    parser.add_argument("--opt", action='store_true', help="Run optimization for the strategy")

    return parser.parse_args()


def main():
    args = get_args()
    if args.qa:
        result = run_backtest(SYMBOL, 2000)
        metric = analyze_strategy_result(result)
        print(metric.json(indent=2))
    elif args.opt:
        opt_df = run_backtest_optimization(SYMBOL, 2020)
        opt_df.sort_values('annual_return', ascending=False, inplace=True)
        print(opt_df.iloc[0])


if __name__ == "__main__":
    main()