from backtrader import Cerebro, analyzers, feeds
from datetime import datetime
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import yfinance as yf
from datetime import datetime
from utils.fancy_log import FancyLogger
from .strategy import MyStrategy
from .base import PerformanceMetrics
import pandas as pd

LOG = FancyLogger(__name__)
INITIAL_CASH = 300

# Cache and rate limit the yahoo finance API
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


def get_sessioned_ticker_for_symbol(symbol: str) -> yf.Ticker:
    session = CachedLimiterSession(
        limiter=Limiter(RequestRate(1, Duration.SECOND)),
        bucket_class=MemoryQueueBucket,
        backend=SQLiteCache("yfinance.cache"),
    )

    return yf.Ticker(symbol, session=session)


def get_stock_data(symbol, start_year: datetime.year):
    start_date = f'{start_year}-01-01'
    # NOTE: to reproduce the LLM response with cache.db, must fix the end_date to a specific date
    end_date = '2024-06-01'
    ticker = get_sessioned_ticker_for_symbol(symbol)
    data = ticker.history(start=start_date, end=end_date, interval='1d')

    return feeds.PandasData(dataname=data)


def run_backtest(symbol: str, target_year: datetime.year, cash=INITIAL_CASH, commission=0.002):
    cerebro = Cerebro()

    cerebro.addstrategy(MyStrategy)
    cerebro.adddata(get_stock_data(symbol, target_year))

    cerebro.addanalyzer(analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(analyzers.Returns, _name='returns')
    cerebro.addanalyzer(analyzers.TradeAnalyzer, _name='trade_analyzer')

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)
    result = cerebro.run()

    return result[0]


def analyze_strategy_result(result):
    sharpe = result.analyzers.sharpe.get_analysis()
    drawdown = result.analyzers.drawdown.get_analysis()
    returns = result.analyzers.returns.get_analysis()
    trade_analyzer = result.analyzers.trade_analyzer.get_analysis()


    return PerformanceMetrics(
        sharpe=sharpe.get('sharperatio', None),
        drawdown=drawdown.get('max', {}).get('drawdown', None),
        annual_return=returns['rnorm100'],
        total_trades=trade_analyzer.get('total', {}).get('total', 0),
        winning_trades=trade_analyzer.get('won', {}).get('total', 0),
        losing_trades=trade_analyzer.get('lost', {}).get('total', 0)
    )


def run_backtest_optimization(
    symbol: str, 
    target_year: datetime.year, 
    cash=INITIAL_CASH, 
    commission=0.002
) -> pd.DataFrame:

    from .params import params_to_optimize
    from itertools import product
    total_combos = len(list(product(*params_to_optimize.values())))
    if total_combos > 20000:
        print(f"parameter combinations exceeded limitation: {total_combos}")
        exit(-1)

    cerebro = Cerebro()

    cerebro.optstrategy(MyStrategy, **params_to_optimize)
    cerebro.adddata(get_stock_data(symbol, target_year))

    cerebro.addanalyzer(analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(analyzers.Returns, _name='returns')
    cerebro.addanalyzer(analyzers.TradeAnalyzer, _name='trade_analyzer')

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)
    result = cerebro.run(maxcpus=20)


    param_list = list(result[0][0].params._getkeys())
    backtest_results = [
        [
            *strategy_result[0].params._getvalues(),
            *analyze_strategy_result(strategy_result[0]).dict().values()
        ]
        for strategy_result in result
    ]

    return pd.DataFrame(
        backtest_results, 
        columns=[
            *param_list,
            *PerformanceMetrics.__fields__.keys()
        ]
    )
    