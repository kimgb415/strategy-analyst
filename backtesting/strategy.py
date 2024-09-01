import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (('bb_period', 20), ('bb_std_dev', 2), ('bb_width_low', 0.05), ('bb_width_high', 0.10), ('position_size', 0.02))

    def __init__(self):
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low

        self.bb = bt.indicators.BBands(self.data_close, period=self.p.bb_period, devfactor=self.p.bb_std_dev)
        self.bbw = (self.bb.lines.top - self.bb.lines.bot) / self.bb.lines.mid

        self.long_signal = bt.And(bt.ind.CrossDown(self.bbw, self.p.bb_width_low), bt.ind.CrossDown(self.data_close, self.bb.lines.bot))
        self.short_signal = bt.And(bt.ind.CrossDown(self.bbw, self.p.bb_width_low), bt.ind.CrossUp(self.data_close, self.bb.lines.top))

        self.long_exit = bt.Or(bt.ind.CrossUp(self.data_close, self.bb.lines.top), bt.ind.CrossUp(self.bbw, self.p.bb_width_high))
        self.short_exit = bt.Or(bt.ind.CrossDown(self.data_close, self.bb.lines.bot), bt.ind.CrossUp(self.bbw, self.p.bb_width_high))

    def next(self):
        if self.position.size == 0:
            if self.long_signal[0]:
                self.buy(size=self.p.position_size * self.broker.cash)
            elif self.short_signal[0]:
                self.sell(size=self.p.position_size * self.broker.cash)
        elif self.position.size > 0:
            if self.long_exit[0]:
                self.close()
        elif self.position.size < 0:
            if self.short_exit[0]:
                self.close()

# Initialize the cerebro
cerebro = bt.Cerebro()

# Add the strategy
cerebro.addstrategy(MyStrategy)

# Run the backtest
cerebro.run()