# get data from upstox
import datetime
from upstox_api.api import *

#s = Session ('8GCicggZzf3OGZ81fzPtY5iMHxNV1bpHqUG7sT29')
#s.set_redirect_uri ('http://127.0.0.1/redirect')
#s.set_api_secret ('py5lqqb79h')
#print(s.get_login_url())

#s.set_code ('77cdbf38c2e5a1694ebc9f44aa24b7d291d6e9b0')

#access_token = s.retrieve_access_token()
#print ('Received access_token: %s' % access_token)
u = Upstox('8GCicggZzf3OGZ81fzPtY5iMHxNV1bpHqUG7sT29', '86f967b47e3469cd647561fbfd6abed93a1a1474')

#print(u.get_balance()) # get balance / margin limits
print(u.get_profile()) # get profile

u.get_master_contract('NSE_EQ') # get contracts for NSE EQ
u.get_master_contract('NSE_FO') # get contracts for NSE FO
u.get_master_contract('NSE_INDEX') # get contracts for NSE INDEX
u.get_master_contract('BSE_EQ') # get contracts for BSE EQ
u.get_master_contract('BSE_INDEX') # get contracts for BSE INDEX
u.get_master_contract('MCX_INDEX') # get contracts for MCX INDEX
u.get_master_contract('MCX_FO') # get contracts for MCX FO
data= u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', 'RELIANCE'), OHLCInterval.Minute_10, datetime.datetime.strptime('01/07/2017', '%d/%m/%Y').date(), datetime.datetime.strptime('07/07/2017', '%d/%m/%Y').date())
print(data)

u.place_order(TransactionType.Buy,  #transaction_type
              u.get_instrument_by_symbol('NSE_EQ', 'UNITECH'),  #instrument
              1,  # quantity
              OrderType.Market,  # order_type
              ProductType.Delivery,  # product_type
              0.0,  # price
              None,  # trigger_price
              0,  # disclosed_quantity
              DurationType.DAY, # duration
              None, # stop_loss
              None, # square_off
              None )# trailing_ticks
