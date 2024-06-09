import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (('period', 20), ('stddev', 2), ('stop_loss_pct', 0.02), ('take_profit_pct', 0.02), ('risk_pct', 0.02))

    def __init__(self):
        self.data_close = self.datas[0].close
        self.sma = bt.indicators.SimpleMovingAverage(self.data_close, period=self.params.period)
        self.stddev = bt.indicators.StandardDeviation(self.data_close, period=self.params.period)
        self.upper_band = self.sma + (self.stddev * self.params.stddev)
        self.lower_band = self.sma - (self.stddev * self.params.stddev)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.data_close[0] <= self.lower_band[0]:
                self.order = self.buy(exectype=bt.Order.Market)
                self.entry_price = self.data_close[0]
            elif self.data_close[0] >= self.upper_band[0]:
                self.order = self.sell(exectype=bt.Order.Market)
                self.entry_price = self.data_close[0]
        else:
            if self.position.size > 0:
                if self.data_close[0] >= self.entry_price * (1 + self.params.take_profit_pct):
                    self.close(exectype=bt.Order.Market)
                elif self.data_close[0] <= self.entry_price * (1 - self.params.stop_loss_pct):
                    self.close(exectype=bt.Order.Market)
            elif self.position.size < 0:
                if self.data_close[0] <= self.entry_price * (1 - self.params.take_profit_pct):
                    self.close(exectype=bt.Order.Market)
                elif self.data_close[0] >= self.entry_price * (1 + self.params.stop_loss_pct):
                    self.close(exectype=bt.Order.Market)

    def stop(self):
        # No need to set anything in the stop method
        pass