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
script_name = 'SBIN'
profit_target = .2  # change the value to test the results, set at 8%
stop_loss = .05  # change the value to test the results, set at 2%
fast_period = 20  # fast moving SMA
slow_period = 50  # slow moving SMA
adx_limit = 35

# get data from nsepy
df = pd.DataFrame(get_history(script_name, start=start_date, end=end_date, index=False))
# plot the closing prices
# plt.plot(df['Close'])
# plt.show()

# variable assignment
position = 0
buy_val = 0
sell_val = 0
last_price = 0
profit = 0
cum_profit = 0

take_profit = 0
stop_loss_val = 0
buy_count = 0
sell_count = 0

df['SMA-FAST'] = TA.SMA(df['Close'], fast_period)
df['SMA-SLOW'] = TA.SMA(df['Close'], slow_period)
df['RSI'] = TA.RSI(df['Close'], 14)
df['ADX'] = TA.ADX(df['High'], df['Low'], df['Close'], 14)
# print(df.tail())

# plotting the smas and the close price
plt.plot(df['Close'], label='Price')
plt.plot(df['SMA-FAST'], label='SMA-FAST')
plt.plot(df['SMA-SLOW'], label='SMA-SLOW')
plt.legend(loc='upper left')
# plt.show()

# print(df.index)

# writing output to a file
f = open('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Output1.csv', 'w')


for i in range(len(df['Close'])):
    last_price = df['Close'][i]
    df['signal'][i] = 'none'
    if i > slow_period:

        # buy entry
        if df['SMA-FAST'][i] >= df['SMA-SLOW'][i] and df['ADX'][i] > adx_limit and position == 0:
            position = 1
            buy_count = buy_count + 1
            buy_val = last_price
            take_profit = buy_val * (1 + profit_target)
            stop_loss_val = buy_val * (1 - stop_loss)
            df['signal'][i] = 'BUY'
            print(df.index[i], ";", "BUY;", last_price, ";", "profit ;", cum_profit, file=f)
        # sell entry
        elif df['SMA-FAST'][i] <= df['SMA-SLOW'][i] and df['ADX'][i] > adx_limit and position == 0:
            sell_val = df['Close'][i]
            take_profit = sell_val * (1 - profit_target)
            stop_loss_val = sell_val * (1 + stop_loss)
            position = -1
            sell_count = sell_count + 1
            df['signal'][i] = 'SELL'
            print(df.index[i], ";", "SELL;", last_price, ";", "profit ;", cum_profit, file=f)

        # already in buy
        elif position == 1 and last_price >= take_profit:
            position = 0
            cum_profit = cum_profit + (last_price - buy_val)
            df['signal'][i] = 'BUY-TP'
            print(df.index[i], ";", "BUY-TP;", last_price, ";", "profit ;", cum_profit, file=f)
        elif position == 1 and last_price <= stop_loss_val:
            position = 0
            cum_profit = cum_profit - (buy_val - last_price)
            df['signal'][i] = 'BUY-SL'
            print(df.index[i], ";", "BUY-STOP LOSS;", last_price, ";", "profit ;", cum_profit, file=f)
        elif position == 1 and last_price <= df['SMA-SLOW'][i]:
            position = 0
            cum_profit = cum_profit - (buy_val - last_price)
            df['signal'][i] = 'BUY-EXIT'
            print(df.index[i], ";", "BUY-Exit;", last_price, ";", "profit ;", cum_profit, file=f)
        elif position == 1 and stop_loss_val <= last_price <= take_profit:
            print(df.index[i], ";", "BUY-HOLD;", last_price, ";", "profit ;", cum_profit, file=f)

        # already in Sell
        elif position == -1 and last_price <= take_profit:
            position = 0
            cum_profit = cum_profit + (sell_val - sell_val)
            df['signal'][i] = 'SELL-TP'
            print(df.index[i], ";", "SELL-TP;", last_price, ";", "profit ;", cum_profit, file=f)
        elif position == -1 and last_price >= stop_loss_val:
            position = 0
            cum_profit = cum_profit - (last_price - sell_val)
            df['signal'][i] = 'SELL-SL'
            print(df.index[i], ";", "SELL-STOP LOSS;", last_price, ";", "profit ;", cum_profit, file=f)
        elif position == -1 and last_price >= df['SMA-SLOW'][i]:
            position = 0
            cum_profit = cum_profit - (last_price - sell_val)
            df['signal'][i] = 'SELL-EXIT'
            print(df.index[i], ";", "SELL-Exit;", last_price, ";", "profit ;", cum_profit, file=f)
        elif position == -1 and stop_loss_val >= last_price >= take_profit:
            print(df.index[i], ";", "Sell-HOLD;", last_price, ";", "profit ;", cum_profit, file=f)


print(df.tail())
print(script_name, ': Buys=', buy_count, 'Sells=', sell_count, "Profits=", cum_profit)

df.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/export.csv')
