import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('maperiod', 20),  # 20-day moving average
        ('bbperiod', 20),  # 20-day Bollinger Bands
        ('bbstddev', 2),  # 2 standard deviations for Bollinger Bands
        ('maxbbdistance', 2),  # maximum distance from MA20 for long/short entry
        ('maxdays', 5),  # maximum days without touching MA20 for long/short entry
        ('exitpct', 0.1),  # 10% profit/loss for exit
    )

    def __init__(self):
        # Initialize moving averages
        self.moving_avg_20 = bt.indicators.MovingAverageSimple(self.data.close, period=self.p.maperiod)
        self.moving_avg_50 = bt.indicators.MovingAverageSimple(self.data.close, period=50)

        # Initialize Bollinger Bands
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.p.bbperiod, devfactor=self.p.bbstddev)

        # Initialize variables for long/short entry and exit
        self.long_entry = False
        self.short_entry = False
        self.position_size = 0

        # Initialize crossover indicators
        self.crossover = bt.indicators.CrossOver(self.moving_avg_20, self.data.close)

    def next(self):
        # Check for long entry
        if not self.long_entry and not self.short_entry:
            if self.data.close > self.moving_avg_50 and self.data.close > self.bb.top:
                if self.crossover > 0:
                    self.long_entry = True
                    self.position_size = self.broker.getcash() * 0.1  # 10% of cash for long position

        # Check for short entry
        if not self.long_entry and not self.short_entry:
            if self.data.close < self.moving_avg_50 and self.data.close < self.bb.mid:
                if self.crossover < 0:
                    self.short_entry = True
                    self.position_size = self.broker.getcash() * 0.1  # 10% of cash for short position

        # Check for exit
        if self.position_size > 0:
            if self.data.close > self.position_size * (1 + self.p.exitpct) or self.data.close < self.position_size * (1 - self.p.exitpct):
                self.close()
                self.long_entry = False
                self.position_size = 0
        elif self.position_size < 0:
            if self.data.close < self.position_size * (1 - self.p.exitpct) or self.data.close > self.position_size * (1 + self.p.exitpct):
                self.close()
                self.short_entry = False
                self.position_size = 0