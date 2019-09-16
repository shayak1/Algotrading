import datetime as dt
import pandas as pd
from nsepy import get_history
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import talib as TA
# import numpy as np

start_date = dt.datetime(2016, 1, 1)
end_date = dt.datetime.today()

# get data from nsepy
df = pd.DataFrame(get_history('SBIN', start=start_date, end=end_date,index=False))
# plot the closing prices
# plt.plot(df['Close'])
# plt.show()


# creating the variables for indicators using talib
fast_period = 20
slow_period = 100

df['SMA-FAST'] = TA.SMA(df['Close'], fast_period)
df['SMA-SLOW'] = TA.SMA(df['Close'], slow_period)

# print(df.tail())

# plotting the smas and the close price
plt.plot(df['Close'], label='Price')
plt.plot(df['SMA-FAST'], label='SMA-FAST')
plt.plot(df['SMA-SLOW'], label='SMA-SLOW')
plt.legend(loc='upper left')
plt.show()

#print(df.index)

# writing output to a file
f = open('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Output.csv','w')

# create variable buy sell signal
position = 0
buy_val = 0
Sell_val = 0
last_price = 0
profit = 0
cum_profit = 0
profit_target = 8
stop_loss = 2
take_profit = 0
Stop_loss_val = 0

for i in range(len(df['Close'])):
    if i > slow_period:
        last_price = df['Close'][i]
        if df['SMA-FAST'][i] > df['SMA-SLOW'][i] and position == 0:
            position = 1
            profit = 0
            buy_val = last_price
            cum_profit = cum_profit + profit
            take_profit = buy_val * (1 + profit_target/100)
            Stop_loss_val = buy_val * (1 - stop_loss/100)
            print(df.index[i], ";", 'BUY', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)

        elif df['SMA-FAST'][i] > df['SMA-SLOW'][i] and position == 1:
            profit = last_price - buy_val
            # checking if profit target already met
            if last_price >= take_profit:
                cum_profit = cum_profit + profit
                position = 0
                print(df.index[i], ";", 'BUY TP', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)
            else:
                print(df.index[i], ";", 'BUY HOLD', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)

        elif df['SMA-FAST'][i] < df['SMA-SLOW'][i] and position == 1:
            profit = last_price - buy_val
            cum_profit = cum_profit + profit
            position = 0
            if last_price <= Stop_loss_val:
                print(df.index[i], ";", 'BUY STOP-LOSS', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)
            else:
                print(df.index[i], ";", 'BUY SO', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)

        elif df['SMA-FAST'][i] < df['SMA-SLOW'][i] and position == 0:
            position = -1
            Sell_val = last_price
            profit = 0
            cum_profit = cum_profit + profit
            take_profit = Sell_val * (1 - profit_target / 100)
            Stop_loss_val = Sell_val * (1 + stop_loss / 100)
            print(df.index[i], ";", 'Sell', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)

        elif df['SMA-FAST'][i] < df['SMA-SLOW'][i] and position == -1:
            profit = Sell_val - last_price
            # checking if profit target already met
            if last_price <= take_profit:
                cum_profit = cum_profit + profit
                position = 0
                print(df.index[i], ";", 'SELL TP', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)
            else:
                print(df.index[i], ";", 'SELL HOLD', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)

        else:
            profit = Sell_val - last_price
            cum_profit = cum_profit + profit
            position = 0
            if last_price >= Stop_loss_val:
                print(df.index[i], ";", 'SELL STOP-LOSS', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)
            else:
                print(df.index[i], ";", 'SELL SO', ";", "LTP", last_price, ";", profit, ";", cum_profit, file=f)






df.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/export.csv')