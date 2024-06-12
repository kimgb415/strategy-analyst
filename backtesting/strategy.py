import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('period_sma', 20),
        ('period_bb', 20),
        ('devfactor', 2.0),
        ('period_rsi', 10),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('risk_pct', 0.015),
        ('stop_loss_pct', 0.03),
        ('max_daily_loss_pct', 0.01)
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.period_sma)
        self.bb = bt.indicators.BollingerBands(self.data, period=self.params.period_bb, devfactor=self.params.devfactor)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data, period=self.params.period_rsi, safediv=True)

        self.position_size = self.params.risk_pct * self.broker.get_value()

    def next(self):
        if self.position.size == 0:
            if self.rsi < self.params.rsi_low and self.data.close < self.bb.bot:
                self.sell(exectype=bt.Order.Market, size=self.position_size)
            elif self.rsi > self.params.rsi_high and self.data.close > self.bb.top:
                self.buy(exectype=bt.Order.Market, size=self.position_size)

        elif self.position.size > 0:
            if self.data.close < self.sma or self.rsi < 50:
                self.close(exectype=bt.Order.Market)

        elif self.position.size < 0:
            if self.data.close > self.sma or self.rsi > 50:
                self.close(exectype=bt.Order.Market)

    def stop(self):
        daily_pnl = self.broker.get_value() - self.broker.startingcash
        daily_pnl_pct = daily_pnl / self.broker.startingcash
        if daily_pnl_pct < -self.params.max_daily_loss_pct:
            self.env.runstop()