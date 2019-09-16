'''
Upstox Python automation
Code- Pyhton
Created by - Shayak Roy
Created on - 29/8/19
API- Upstox Developer APIs
Trade automation with user interaction
'''

# Schedule Library imported
import schedule
import time

# importing required packages
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

# import modules from Upstox
from upstox_api import *
from upstox_api.api import *

# for datetime utilities
import datetime as dt
from datetime import timedelta

# for webdriver and login automation
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse

# for technical indicators
import talib as TA

import os, sys
from tempfile import gettempdir

import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# store key variables for api access
api_info = dict([('api_key', '8GCicggZzf3OGZ81fzPtY5iMHxNV1bpHqUG7sT29'),
                 ('api_secret', 'py5lqqb79h'),
                 ('redirect_url', 'http://127.0.0.1/redirect')])

# store key variables for login
login_info = dict([('login_id', '214062'),
                   ('password1', 'Shayak@28feb'),
                   ('2fa', '1986')])

# defining global vars
u = None
s = None
profile = None
code = None
logged_in = False

historic_data = pd.DataFrame()
fast_period = 5
med_period = 20  # to be used as trigger
slow_period = 50

sma_diff_limit = 50

script_name = 'CRUDEOIL19SEPFUT'
exchange = 'MCX_FO'
instrument = ''
quantity = 100
profit_target = 90  # change the value to test the results, set at 8%
stop_loss_target = 45  # change the value to test the results, set at 2%
trailing = 20
adx_limit = 20


# browser automation for granting access and to get the code for login
def login():

    # fetching access toke from login
    global code, u, s, logged_in

    browser = webdriver.Chrome('/Users/shayakroy/anaconda3/lib/python3.7/chromedriver')
    browser.get('https://api.upstox.com/index/dialog/authorize?apiKey={}&redirect_uri={}&response_type=code'.format(api_info['api_key'], api_info['redirect_url']))
    browser.implicitly_wait(20)
    browser.find_element_by_name('username').send_keys(login_info['login_id'] + Keys.ENTER)
    browser.implicitly_wait(10)
    browser.find_element_by_name('password').send_keys(login_info['password1'] + Keys.ENTER)
    browser.implicitly_wait(10)
    browser.find_element_by_name('password2fa').send_keys(login_info['2fa'] + Keys.ENTER)
    browser.implicitly_wait(10)
    browser.find_element_by_id('allow').click()
    browser.implicitly_wait(10)
    get_code = urlparse(browser.current_url)
    browser.quit()  # kill the browser
    code = get_code.query.split('code=', 1)[1]
    if code != "":
        print('code fetched successfully')

    else:
        print('Error fetching code')
    return code     # code from the login access


def session():
    global code, profile, access_token, logged_in, s, u
    s = Session(api_info['api_key'])
    s.set_redirect_uri(api_info['redirect_url'])
    s.set_api_secret(api_info['api_secret'])
    access_token = read_key_from_settings1('access_token')
    print(access_token)
    if access_token is not None:
        try:
            u = Upstox(api_info['api_key'], access_token)  # establish an active session
            logged_in = True
            print('existing access token used for login')

        except:
            print('Retry login')
            code = login()
            s.set_code(code)
            access_token = s.retrieve_access_token()
            write_key_to_settings1('access_token', access_token)
            u = Upstox(api_info['api_key'], access_token)

    else:
        print('New login')
        code = login()
        s.set_code(code)
        access_token = s.retrieve_access_token()
        write_key_to_settings1('access_token', access_token)

    print("Login successful")


def load_profile():
    global profile, u
    profile = u.get_profile()
    print('Welcome', profile['name'])
    balance = u.get_balance()
    print('Equity Bal:', balance['equity']['ledger_balance'],
          '\nCommodity Bal:', balance['commodity']['ledger_balance'])

# Storing the access token to avoid login in


def get_master_contracts():
    global u

    u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ
    u.get_master_contract('NSE_FO')  # get contracts for NSE FO
    u.get_master_contract('NSE_INDEX')  # get contracts for NSE INDEX
    u.get_master_contract('MCX_FO')  # get contracts for MCX FO


def get_historic_data():
    global u, historic_data, script_name, exchange, instrument
    current_date = dt.date.today()
    instrument = u.get_instrument_by_symbol(exchange, script_name)

    # extracting 6 days of data as max limit is 6
    for i in range(1, 8):
        end = current_date - timedelta(days=(i - 1) * 6)
        start = end - timedelta(days=5)
        df1 = pd.DataFrame(u.get_ohlc(instrument, OHLCInterval.Minute_30, start, end))

        if i == 1:
            historic_data = df1

        else:
            df2 = pd.concat([df1, historic_data], ignore_index=True)
            historic_data = df2
            # print(df2)

    time_format()

'''
    # checking if the data pull is complete
    last_date = historic_data.index[-1]
    print(last_date, current_date)
    print('Data Pull successful')
    if last_date.day != current_date.day:
        print(1)
'''


def time_format():
    global historic_data
    # print('*****-----Formatting the time---*****')
    # convert the timestamp to integer and then iterate to convert to date-time value
    historic_data['timestamp'] = historic_data['timestamp'].astype('int')
    historic_data['open'] = historic_data['open'].astype('float')
    historic_data['high'] = historic_data['high'].astype('float')
    historic_data['low'] = historic_data['low'].astype('float')
    historic_data['close'] = historic_data['close'].astype('float')

    for i in range(len(historic_data.index)):
        # print(i, dt.datetime.fromtimestamp(historic_data['timestamp'][i]/1000))
        historic_data['timestamp'][i] = dt.datetime.fromtimestamp(historic_data['timestamp'][i]/1000)

    # set time as index
    historic_data.set_index([historic_data['timestamp']], inplace=True)
    historic_data.index.name = 'time'
    historic_data.drop(['timestamp'], axis=1, inplace=True)

    # print('*****-----Formatting the time complete---*****')

    # print(historic_data)


def indicators():
    global historic_data
    historic_data['fast_sma'] = TA.SMA(historic_data['close'], fast_period)
    historic_data['slow_sma'] = TA.SMA(historic_data['close'], slow_period)
    historic_data['med_sma'] = TA.SMA(historic_data['close'], med_period)
    historic_data['adx'] = TA.ADX(historic_data['high'],
                                  historic_data['low'],
                                  historic_data['close'], 14)
    sma = historic_data['slow_sma']
    historic_data['sma_diff'] = historic_data['fast_sma'].sub(other=sma, fill_value=500)


def decision():
    global historic_data, u, slow_period, fast_period, adx_limit, stop_loss_target, profit_target, trailing
    buy_count = 0
    sell_count = 0
    cum_profit = 0

    position = 0
    take_profit = 0
    stop_loss_val_buy = 0
    stop_loss_val_sell = 0
    buy_val = 0
    sell_val = 0
    buy_loss_count = 0
    sell_loss_count = 0
    buy_profit_count = 0
    sell_profit_count = 0
    max_profit_buy = 0
    max_loss_buy = 0
    max_profit_sell = 0
    max_loss_sell = 0
    cum_profit_buy = 0
    cum_profit_sell = 0
    cum_loss_buy = 0
    cum_loss_sell = 0

    df = historic_data
    df['signal'] = ''
    df['net'] = 0
    for i in range(len(df['close'])):
        df['signal'][i] = 'No Signal'
        last_price = df['close'][i]
        write_key_to_settings1('last_price', last_price)
        if i > slow_period:  # Skipping the periods with missing slow SMA values
            if position == 0:
                if df['close'][i] > df['med_sma'][i] and 0 <= df['sma_diff'][i] <= sma_diff_limit and df['adx'][i] > adx_limit:
                    # place order for buy
                    buy_val = last_price
                    stop_loss_val_buy = buy_val - stop_loss_target  # place a stop loss order at this price
                    # stop_loss_val_buy = round(buy_val * (1 - stop_loss_target))  # place a stop loss order at this price
                    take_profit = buy_val + profit_target
                    position = 1
                    buy_count = buy_count + 1
                    df['signal'][i] = 'buy-entry'
                    # storing the last traded values
                    store_last_trade('buy-entry', buy_val, stop_loss_val_buy, take_profit)

                elif df['close'][i] < df['med_sma'][i] and (-1 * sma_diff_limit) <= df['sma_diff'][i] <= 0 and df['adx'][i] > adx_limit:
                    # place sell order
                    sell_val = last_price
                    stop_loss_val_sell = sell_val + stop_loss_target  # place a stop loss order at this price
                    # stop_loss_val_sell = round(sell_val * (1 + stop_loss_target))  # place a stop loss order at this price
                    take_profit = sell_val - profit_target
                    position = -1
                    sell_count = sell_count + 1
                    df['signal'][i] = 'sell-entry'

                    # storing the last traded values
                    store_last_trade('sell-entry', sell_val, stop_loss_val_sell, take_profit)

            elif position == 1:
                if last_price >= take_profit:
                    df['signal'][i] = 'buy-TP'  # reaches profit target
                    position = 0
                    store_last_trade('buy-TP', last_price, 0, 0)

                    profit = (last_price - buy_val)
                    buy_profit_count += 1
                    cum_profit = cum_profit + profit
                    max_profit_buy = max(max_profit_buy, profit)
                    cum_profit_buy = cum_profit_buy + profit

                elif last_price <= df['slow_sma'][i]:  # crosses slow moving SMA
                    df['signal'][i] = 'buy-exit'
                    position = 0
                    store_last_trade('buy-exit', last_price, 0, 0)

                    profit = (last_price - buy_val)
                    cum_profit = cum_profit + profit

                    if profit > 0:
                        cum_profit_buy = cum_profit_buy + profit
                        buy_profit_count += 1

                    else:
                        cum_loss_buy = cum_loss_buy + abs(profit)
                        buy_loss_count += 1

                elif df['low'][i] <= stop_loss_val_buy:
                    df['signal'][i] = 'buy-exit-SL'  # hits stop loss
                    position = 0
                    store_last_trade('buy-exit-SL', stop_loss_val_buy, 0, 0)
                    profit = (last_price - buy_val)
                    cum_profit = cum_profit + profit

                    if profit > 0:
                        cum_profit_buy = cum_profit_buy + profit
                        buy_profit_count += 1

                    else:
                        cum_loss_buy = cum_loss_buy + abs(profit)
                        buy_loss_count += 1

                else:
                    df['signal'][i] = 'buy-hold'

                    price_diff = last_price - stop_loss_val_buy - stop_loss_target
                    if price_diff > 0 and (price_diff/trailing) > 1:
                        stop_loss_val_buy = stop_loss_val_buy + price_diff / trailing * trailing
                        df['signal'][i] = 'buy-SL-trailing'
                        write_key_to_settings1('SL', stop_loss_val_buy)

            elif position == -1:
                if last_price <= take_profit:  # reaches profit target
                    df['signal'][i] = 'sell-TP'
                    position = 0
                    store_last_trade('sell-TP', last_price, 0, 0)

                    profit = (sell_val - last_price)
                    cum_profit = cum_profit + profit
                    sell_profit_count += 1
                    max_profit_sell = max(max_profit_sell, profit)
                    cum_profit_sell = cum_profit_sell + profit

                elif last_price >= df['slow_sma'][i]:  # crosses above slow moving SMA
                    df['signal'][i] = 'sell-exit'
                    position = 0
                    store_last_trade('sell-exit', last_price, 0, 0)

                    profit = (sell_val - last_price)
                    cum_profit = cum_profit + profit

                    if profit > 0:
                        cum_profit_sell = cum_profit_sell + profit
                        sell_profit_count += 1

                    else:
                        cum_loss_sell = cum_loss_sell + abs(profit)
                        sell_loss_count += 1

                elif df['high'][i] >= stop_loss_val_sell:  # hits stop loss
                    df['signal'][i] = 'sell-exit-SL'
                    position = 0

                    store_last_trade('sell-exit-SL', stop_loss_val_sell, 0, 0)

                    profit = (sell_val - last_price)
                    cum_profit = cum_profit + profit

                    if profit > 0:
                        cum_profit_sell = cum_profit_sell + profit
                        sell_profit_count += 1

                    else:
                        cum_loss_sell = cum_loss_sell + abs(profit)
                        sell_loss_count += 1

                    profit = sell_val - stop_loss_val_sell
                    cum_profit = cum_profit + profit
                    sell_loss_count += 1
                    cum_loss_sell = cum_loss_sell + abs(profit)
                    max_loss_sell = max(max_loss_sell, abs(profit))

                else:
                    df['signal'][i] = 'sell-hold'

                    price_diff = stop_loss_val_buy - last_price - stop_loss_target
                    if (price_diff / trailing) > 1:
                        df['signal'][i] = 'sell-SL-trailing'
                        stop_loss_val_buy = stop_loss_val_buy - price_diff / trailing * trailing
                        write_key_to_settings1('SL', stop_loss_val_sell)

        df['net'][i] = cum_profit_buy + cum_profit_sell - cum_loss_buy - cum_loss_sell

    historic_data = df

    # summary of back testing
    net = cum_profit_buy + cum_profit_sell - cum_loss_buy - cum_loss_sell

    print(script_name, ': Buys=', buy_count, 'Sells=', sell_count, "Profits=", net)

    print('\n-----buy summary----')
    print('buy_count:', buy_count, ' win:', buy_profit_count, ' avg profit:', cum_profit_buy/buy_profit_count, ' avg loss:', round(cum_loss_buy/buy_loss_count))
    print('\n-----sell summary----')
    print('sell_count:', sell_count, ' win:', sell_profit_count, ' avg profit:', cum_profit_sell/sell_profit_count, ' avg loss:', round(cum_loss_sell/sell_loss_count))

    # return the last decision, check the column number incase new vars are added
    write_key_to_settings1('signal', df.iloc[-1, -2])
    return df.iloc[-1, -2]
    # return 'sell-entry'


def store_last_trade(entry, price, sl, target):
    # storing the last traded values
    write_key_to_settings1('last_trade', entry)
    write_key_to_settings1('trade_price', round(price))
    write_key_to_settings1('SL', round(sl))
    write_key_to_settings1('target', round(target))


def trade():
    # check if there is an ongoing trade
    global u, exchange, script_name, instrument
    # trade_pos = pd.DataFrame(u.get_positions())
    action = decision()
    if action != 'No Signal':
    # if trade_pos.empty:

        if action == "buy-entry":
            print('placing order for Buy Entry')
            sl = read_key_from_settings1('SL')
            # df_buy_entry = u.place_order('b', instrument, quantity=10, order_type='M', product_type='D')
            # print(df_buy_entry)
            # placing stop loss order
            # df_buy_sl = u.place_order('s', instrument, quantity=10, order_type='SL', product_type='D', price=round(sl))
            # write_key_to_settings1('sl-id', df_buy_sl['order_id'])

        elif action == "sell-entry":
            print('placing order for Sell Entry')
            sl = read_key_from_settings1('SL')
            # df_sell_entry = u.place_order('s', instrument, quantity=10, order_type='M', product_type='D')
            # print(df_sell_entry)
            # placing stop loss order
            # df_sell_sl = u.place_order('s', instrument, quantity=10, order_type='SL', product_type='D', price=round(sl))
            # write_key_to_settings1('sl-id', df_sell_sl['order_id'])


        elif action == 'buy-exit':
            print('placing order for Buy exit')
            print('placing order for cancelling stop loss order')
            # df_buy_exit = u.place_order('s', instrument, quantity=10, order_type='M', product_type='D')
            # print(df_buy_exit)
            # cancel stop loss order
            # df_cancel_sl = u.order_cancel(read_key_from_settings1('sl-id'))
            # print(df_cancel_sl)

        elif action == 'sell-exit':
            print('placing order for Sell exit')
            print('placing order for cancelling stop loss order')
            # df_buy_exit = u.place_order('b', instrument, quantity=10, order_type='M', product_type='D')
            # print(df_buy_exit)
            # cancel stop loss order
            # df_cancel_sl = u.order_cancel(read_key_from_settings1('sl-id'))
            # print(df_cancel_sl)

        elif action == "buy-TP":
            print('placing order for Buy TP')
            print('cancel SL order')
            # df_buy_tp = u.place_order('s', instrument, quantity=10, order_type='M', product_type='D')
            # print(df_buy_tp)
            # cancel stop loss order
            # df_cancel_sl = u.order_cancel(read_key_from_settings1('sl-id'))

        elif action == "sell-TP":
            print('placing order for Sell TP')
            print('cancel SL order')
            # df_buy_tp = u.place_order('b', instrument, quantity=10, order_type='M', product_type='D')
            # print(df_buy_tp)
            # cancel stop loss order
            # df_cancel_sl = u.order_cancel(read_key_from_settings1('sl-id'))

        elif action == "buy-SL-trailing":
            sl = read_key_from_settings1('SL')
            print('modifying SL order to ', sl)
            # df_buy_sl = u.modify_order(order_id=read_key_from_settings1('sl-id'), price=round(sl))

        elif action == "sell-SL-trailing":
            sl = read_key_from_settings1('SL')
            print('modifying SL order to ', sl)
            # df_sell_sl = u.modify_order(order_id=read_key_from_settings1('sl-id'), price=round(sl))

    trade_pos()  # show current position


def write_key_to_settings1(key, value):
    filename = os.path.join(gettempdir(), 'interactive_api.json')
    try:
        file = open(filename, 'r')
    except IOError:
        data = {"last_trade": "", 'trade_price': None, 'SL': None, 'target': None, "access_token": "",
                'last_price': None, 'signal': '', 'sl_id': None}
        with open(filename, 'w') as output_file:
            json.dump(data, output_file)
    file = open(filename, 'r')
    try:
        data = json.load(file)
    except:
        data = {}
    data[key] = value
    with open(filename, 'w') as output_file:
        json.dump(data, output_file)


def read_key_from_settings1(key):
    filename = os.path.join(gettempdir(), 'interactive_api.json')
    try:
        file = open(filename, 'r')
    except IOError:
        file = open(filename, 'w')
    file = open(filename, 'r')
    try:
        data = json.load(file)
        return data[key]
    except:
        pass
    return None


'''
def graph():
    df = historic_data


    # Converting date to pandas datetime format
    import matplotlib.dates as mdates
    from mpl_finance import candlestick_ohlc
    df['date1'] = pd.to_datetime(df.index)
    df['date1'] = df['date1'].apply(mdates.date2num)

    # Creating required data in new DataFrame OHLC
    ohlc = df[['open', 'high', 'low', 'close']].copy()
    ohlc['slow_sma'] = df['slow_sma']
    ohlc['fast_sma'] = df['fast_sma']

    f1, ax = plt.subplots(figsize=(10, 2))
    # plot the candlesticks
    candlestick_ohlc(ax, ohlc.values, width=.1, colorup='green', colordown='red')
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    #ax.plot(ohlc['date1'], ohlc['fast_sma'], color='green', label='sma_fast')
    #ax.plot(ohlc['date1'], ohlc['slow_sma'], color='cyan', label='sma_slow')

    plt.show()

# using plotly module
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Candlestick(open=df['open'], high=df['high'],
                                         low=df['low'], close=df['close'],
                                         increasing_line_color='green',
                                         decreasing_line_color='red')])
    fig.show()
'''


def trade_pos():
    trade_type = read_key_from_settings1('last_trade')
    sl = read_key_from_settings1('SL')
    target = read_key_from_settings1('target')
    price = read_key_from_settings1('trade_price')
    # last = read_key_from_settings1('last_price')
    signal = read_key_from_settings1('signal')
    ltp = live_data()

    if signal in ('No Signal', 'sell-TP', 'buy-TP', 'sell-exit', 'buy-exit', 'sell-SL', 'buy-SL'):
        print('Last signal: {}.'.format(signal), 'Waiting for new trade')
    elif trade_type == 'buy-entry':
        gain = ltp - price
        print('\nlast trade:', trade_type, "@", price, " SL:", sl,
              ' target:', target, ' ltp:', ltp, ' PnL:', gain, '\nsignal:', signal)
    elif trade_type == 'sell-entry':
        gain = price - ltp
        print('\nlast trade:', trade_type, "@", price, " SL:", sl,
              ' target:', target, ' ltp:', ltp, ' PnL:', gain, '\nsignal:', signal)


def live_data():
    global u, instrument
    df = u.get_live_feed(instrument, LiveFeedType.LTP)
    return df['ltp']


def order_place():
    instrument1 = u.get_instrument_by_symbol('NSE_EQ', 'SBIN')
    df = u.place_order('b', instrument1, quantity=1, order_type='L', product_type='D', price=287.0)


    # id1 = int(df['order_id'])
    # print(df)
    # print(id1)
    # df=u.modify_order(order_id=190916000185783, price=287.5)
    df = u.cancel_order(190916000185783)

    print(df)


def main():

    session()
    load_profile()
    print("local time: ", dt.datetime.now().strftime('%X'),'\n')
    # print('*****------initializing master_contracts------******')
    # print('*****------initializing data pull------******')
    get_master_contracts()
    get_historic_data()
    indicators()
    decision()


    # trade()

    # trade_pos()

    # order_place()

    df = historic_data
    print(df.tail(2))
    # graph()
    historic_data.to_excel('/Users/shayakroy/Desktop/Trading Videos/Pyhton/data.xlsx')
    live_data()


if __name__ == '__main__':
    main()


# hide the above 2 lines and run the below lines for scheduling
'''
schedule.every().hour.at(":00").do(main)
schedule.every().hour.at(":30").do(main)

while True:
    schedule.run_pending()
    time.sleep(1)

'''