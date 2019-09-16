
import pandas as pd
import datetime as dt
from datetime import timedelta
from nsepy import get_history
import talib as TA


# get futures data for 2 different expiry
# merge data into one file
# create the ratio of the 2 prices
# form a normal distribution for each observation
# basis the normal distribution create flags for buy, buy exit, sell and sell exit
# calculate and print the profit from each trade (buy-buy-exit, sell-sell-exit)

df_futures = pd.DataFrame()
df_futures_next = pd.DataFrame()
def get_futures_data():
    global df_futures
    global df_futures_next
    df_futures = pd.DataFrame(get_history(symbol="SBIN",
                            start=dt.datetime(2019, 5, 1),
                            end=dt.datetime(2019, 8, 1),
                            futures=True,
                            expiry_date=dt.datetime(2019, 7, 25)))
    df_futures.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Pair Trading/futures1.csv')
    # print(df_futures)
    df_futures.drop(columns=['Open', 'High', 'Low', 'Settle Price', 'Number of Contracts', 'Turnover', 'Open Interest','Change in OI', 'Last'], axis=1, inplace= True)


    df_futures_next = pd.DataFrame(get_history(symbol="SBIN",
                            start=dt.datetime(2019, 5, 1),
                            end=dt.datetime(2019, 8, 1),
                            futures=True,
                            expiry_date=dt.datetime(2019, 8, 29)))
    df_futures_next.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Pair Trading/futures2.csv')
    # print(df_futures_next)
    df_futures_next.drop(columns=['Open', 'High', 'Low', 'Settle Price', 'Number of Contracts', 'Turnover', 'Open Interest', 'Change in OI', 'Underlying', 'Symbol', 'Last'], axis=1, inplace=True)
    df_futures_next.rename(columns={'Expiry': 'Expiry_next', 'Close': 'Close_Next'}, inplace=True)


get_futures_data()


def merge():
    global df_futures
    global df_futures_next
    # print(df_futures_next.tail())
    # print(df_futures.tail())

    df_futures.join(df_futures_next)
    # print(df_merged.tail())
    df_merged = pd.concat([df_futures, df_futures_next], axis=1, sort=True)
    # print(df_futures.tail(15))
    # print(df_merged.tail(15))
    df_merged['ratio'] = df_merged['Close']/df_merged['Close_Next']
    df_merged.drop(columns=['Expiry_next'], axis=1, inplace=True)
    df_merged.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Pair Trading/merged.csv')

merge()
