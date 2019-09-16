
from nsepy import get_history
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

start_date = dt.datetime(2018, 1, 1)
end_date = dt.datetime.today()



#define each and everything to perform the operation
def PPSR(data):
    PP = pd.Series((data['High'] + data['Low'] + data['Close']) / 3)
    R1 = pd.Series(2 * PP - data['Low'])
    S1 = pd.Series(2 * PP - data['High'])
    R2 = pd.Series(PP + data['High'] - data['Low'])
    S2 = pd.Series(PP - data['High'] + data['Low'])
    R3 = pd.Series(data['High'] + 2 * (PP - data['Low']))
    S3 = pd.Series(data['Low'] - 2 * (data['High'] - PP))
    psr = {'PP':PP, 'R1':R1, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3}
    PSR = pd.DataFrame(psr)
    data= data.join(PSR)
    return data
#extract the stock data
data = pd.DataFrame(get_history("SBIN", start= start_date, end= end_date))
#compute and print the data
LL=PPSR(data)
print(LL)
# plot the data
pd.concat([data['Close'], pd.PP, pd.R1, pd.S1,PD.R2, pd.S2, pd.R3, pd.S3],axis=1).plot(figsize=(12,9),grid=True)
plt.show()
