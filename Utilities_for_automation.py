import pandas as pd

from datetime import datetime
from dateutil import tz
import pytz
to_zone = tz.tzlocal()
from datetime import timedelta

from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import talib as TA


def headless():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")


from upstox_api.api import *

timestamp = 1545730073
timestamp2 = 1566444600000
timestamp1 = timestamp2/1000
dt_object = datetime.fromtimestamp(timestamp)
dt_object1 = datetime.fromtimestamp(timestamp1)
dt_object2 = datetime.utcfromtimestamp(timestamp1)
dt_object3 = dt_object2.astimezone(to_zone)


print("dt_object =", dt_object)
print("dt_object1 =", dt_object1)
print("dt_object2 =", dt_object2)
print("dt_object3 =", dt_object3)

print("type(dt_object) =", type(dt_object))

# parsing the URL
parsed = urlparse('http://127.0.0.1/redirect?code=f623f66e7e57202e594b129206c18e679142e6ca')
print(parsed.query.split('code=', 1)[1])
print(parsed.query[5:])

redirect_url = 'http://127.0.0.1/redirect'
api_key = '8GCicggZzf3OGZ81fzPtY5iMHxNV1bpHqUG7sT29'
api_secret = 'py5lqqb79h'


login_id = '214062'
password1 = 'Shayak@28feb'
password2 = '1986'
code = ''

def login():
    global code

    browser = webdriver.Chrome('/Users/shayakroy/anaconda3/lib/python3.7/chromedriver')
    browser.get('https://api.upstox.com/index/dialog/authorize?apiKey={}&redirect_uri={}&response_type=code'.format(api_key, redirect_url))
    browser.implicitly_wait(20)
    browser.find_element_by_name('username').send_keys(login_id + Keys.ENTER)
    browser.implicitly_wait(10)
    browser.find_element_by_name('password').send_keys(password1 + Keys.ENTER)
    browser.implicitly_wait(10)
    browser.find_element_by_name('password2fa').send_keys(password2 + Keys.ENTER)
    browser.implicitly_wait(10)
    browser.find_element_by_id('allow').click()
    browser.implicitly_wait(10)
    get_code = urlparse(browser.current_url)
    print(get_code.query.split('code=', 1)[1])
    code = get_code.query.split('code=', 1)[1]
    return code
    # browser.quit()

# login()

# establish an upstox session
def session():
    s = Session(api_key)
    s.set_redirect_uri(redirect_url)
    s.set_api_secret(api_secret)
    print(s.get_login_url())
    code = login()
    s.set_code(code)
    access_token = s.retrieve_access_token()
    u = Upstox(api_key, access_token)
    print("Login successful. Verify profile:")
    # print(u.get_profile())
    position = pd.DataFrame(u.get_positions())
    trans = position.T

   #  profit = position['unrealized_profit']
    print(trans)
    # print('\n', profit)
    balance = pd.DataFrame(u.get_balance())
    balance1 = balance["commodity"]["available_margin"]
    #print(balance1)
    u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ
    u.get_master_contract('NSE_FO')  # get contracts for NSE FO
    u.get_master_contract('NSE_INDEX')  # get contracts for NSE INDEX
    u.get_master_contract('MCX_FO')  # get contracts for MCX FO
    data = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('MCX_FO', 'CRUDEOILM19SEPFUT'), OHLCInterval.Minute_30,
                      datetime.strptime('21/08/2019', '%d/%m/%Y').date(),
                      datetime.strptime('27/08/2019', '%d/%m/%Y').date()))
    data1 = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('MCX_FO', 'CRUDEOILM19SEPFUT'), OHLCInterval.Minute_30,
                                   datetime.today()-timedelta(days=5),
                                   datetime.today()))
   # print(data1.tail())
    #print(data1.head())
   # print(type(data.index))
    data.set_index('timestamp', inplace=True)
    data['SMA_fast']=TA.SMA(data['close'],20)
    data['SMA_slow'] = TA.SMA(data['close'], 50)
    data['ADX'] = TA.ADX(data['high'],data['low'],data['close'],14)

    #convert timestamp
    # data['time'] = pd.to_datetime(data['timestamp'])

    #print(data.tail())


session()

