import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (('period', 50), ('devfactor', 2.0), ('stop_loss_pct', 0.03), ('take_profit_pct', 0.03), ('max_positions', 5), ('risk_pct', 0.015))

    def __init__(self):
        self.data.close = self.datas[0].close
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
        self.stddev = bt.indicators.StandardDeviation(self.data.close, period=self.params.period)
        self.lower_band = self.sma - self.stddev * self.params.devfactor
        self.upper_band = self.sma + self.stddev * self.params.devfactor
        self.order = None
        self.position_size = self.params.risk_pct * self.broker.get_value()

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.data.close <= self.lower_band:
                self.order = self.buy(exectype=bt.Order.Market, size=self.position_size)
            elif self.data.close >= self.upper_band:
                self.order = self.sell(exectype=bt.Order.Market, size=self.position_size)
        else:
            if self.position.size > 0:
                if self.data.close >= self.upper_band:
                    self.close()
                elif self.data.close <= self.position.price * (1 - self.params.stop_loss_pct):
                    self.close()
            elif self.position.size < 0:
                if self.data.close <= self.lower_band:
                    self.close()
                elif self.data.close >= self.position.price * (1 + self.params.take_profit_pct):
                    self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Rejected, order.Canceled, order.Margin, order.Expired]:
            self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            pass