import time
import backtrader as bt
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import tensorflow as tf


# create simple strategy

class SimpleStrategy(bt.Strategy):
    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),  # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    )
    sess = tf.Session()

    def log(self, txt: object, dt: object = None) -> object:
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders
        self.order = None
        # macd indicator
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        # To set the stop price
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        # Control market trend
        self.sma = bt.indicators.SMA(self.data, period=self.p.smaperiod)
        self.smadir = self.sma - self.sma(-self.p.dirperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED,PRICE %.2f,COST %.2f,COMMISSION %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm)
                         )
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # 测试一下
        print(self.macd[0], self.mcross[0], self.sma[0], self.smadir[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.mcross[0] > 0.0 and self.smadir < 0.0:
                self.order = self.buy()
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist

        else:  # in the market
            pclose = self.data.close[0]
            pstop = self.pstop

            if pclose < pstop:
                self.close()  # stop met - get out
            else:
                pdist = self.atr[0] * self.p.atrdist
                # Update only if greater than
                self.pstop = max(pstop, pclose - pdist)

    def build_q_model(self, input_tensor):
        input_layer = tf.reshape(input_tensor, [-1, num_x, num_t])
        layer1 = tf.layers.conv1d(
            input_layer,
            5,
            (1, 2, 3, 4, 5),
            strides=1,
            padding='same',
            name='firstconv')
        pooling1 = tf.layers.max_pooling1d(layer1, pool_size=1, strides=1, name='firstpolling')
        conv2 = tf.layers.conv1d(pooling1, 5, 3, strides=1, padding='same', name='second')
        pooling2 = tf.layers.max_pooling1d(conv2, 2, 1, padding='same', name='secondpooling')
        flatten1 = tf.reshape(pooling2, [-1, tf.shape(pooling2)[1] * tf.shape(pooling2)[2]])
        dense1 = tf.layers.dense(flatten1, 20, activation=tf.nn.relu)
        dense2 = tf.layers.dense(dense1, units=3)
        return dense2

    def memory_save(self):
        pass

    def greedy_policy(self,sess):
        pass

    def q_policy(self):
        pass


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(SimpleStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas/orcl-1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(1995, 1, 3),
        # Do not pass values before this date
        todate=datetime.datetime(2014, 12, 27),
        # Do not pass values after this date
        nullvalue=0.0,

        dtformat=('%Y-%m-%d'),
        # tmformat=('%H:%M:%S'),

        datetime=0,
        # time=1,
        high=2,
        low=3,
        open=4,
        close=5,
        volume=6,
        openinterest=-1
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start and commission 笑脸
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
