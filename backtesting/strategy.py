import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (('period_ema', 20), ('period_rsi', 14), ('std_dev', 1.5), ('atr_multiplier', 1.5),
              ('max_daily_allocation', 0.1), ('max_weekly_allocation', 0.2), ('daily_loss_limit', 0.015),
              ('weekly_loss_limit', 0.03), ('monthly_loss_limit', 0.05))

    def __init__(self):
        self.ema = bt.ind.EMA(self.data.close, period=self.params.period_ema)
        self.std_dev = bt.ind.StdDev(self.data.close, period=self.params.period_ema)
        self.upper_band = self.ema + (self.params.std_dev * self.std_dev)
        self.lower_band = self.ema - (self.params.std_dev * self.std_dev)
        self.rsi = bt.ind.RSI(self.data.close, period=self.params.period_rsi, safediv=True)
        self.atr = bt.ind.ATR(self.data, period=14)
        self.position_size = 0

    def next(self):
        if self.position.size == 0:
            if self.data.close < self.lower_band and self.rsi < 30:
                self.position_size = self.calculate_position_size()
                self.buy(exectype=bt.Order.Market, size=self.position_size)
            elif self.data.close > self.upper_band and self.rsi > 70:
                self.position_size = self.calculate_position_size()
                self.sell(exectype=bt.Order.Market, size=self.position_size)
        else:
            if self.data.close > self.ema + (self.params.atr_multiplier * self.atr):
                self.close()
            elif self.data.close < self.ema - (self.params.atr_multiplier * self.atr):
                self.close()

    def calculate_position_size(self):
        volatility = self.atr / self.data.close
        position_size = (self.params.max_daily_allocation / volatility) * self.broker.getcash()
        return int(position_size)

    def stop(self):
        # Implement risk management and performance metrics calculation here
        pass