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

LOG = FancyLogger(__name__)


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
    end_date = datetime.now().strftime('%Y-%m-%d')
    ticker = get_sessioned_ticker_for_symbol(symbol)
    data = ticker.history(start=start_date, end=end_date, interval='1d')

    return feeds.PandasData(dataname=data)


def run_backtest(symbol: str, target_year: datetime.year, cash=10000, commission=0.002):
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