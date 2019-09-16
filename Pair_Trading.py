from nsepy import get_history
import datetime as dt
import pandas as pd
# import numpy as np
import statistics

# define the period for data comparision
start_date = dt.datetime(2018, 1, 1)
end_date = dt.datetime.today()


# define the pair here
series1 = 'ICICIBANK'
series2 = 'AXISBANK'

df1 = pd.DataFrame(get_history(series1, start=start_date, end=end_date))
df2 = pd.DataFrame(get_history(series2, start=start_date, end=end_date))

df1.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Pair Trading/{}.csv'.format(series1))
df2.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Pair Trading/{}.csv'.format(series2))

# rename the variable
df1.rename(columns={'Close': series1}, inplace=True)
df2.rename(columns={'Close': series2}, inplace=True)

# keeping only the closing prices in the 2 data frames
df1 = df1[series1]
df2 = df2[series2]

# merging the 2 datasets
df3 = pd.concat([df1, df2], axis=1, join='inner')
print(df3.tail())
# getting the ratios of the 2 prices
df3['ratio']=df3[series1]/df3[series2]

corr = df3[series1].corr(df3[series2], method='pearson')
print('correlation:', corr)
print(df3[series1].corr(df3[series2], method='pearson'))
mean_ratio = df3['ratio'].mean()
sd = statistics.stdev(df3['ratio'])
print(mean_ratio, sd)

# check the buy sell conditions
# if corr is positive then both buy, else buy and sell the pair based on the deviation from the mean

position = 0
buy1 = 0
buy2 = 0
sell1 = 0
sell2 = 0
cum_profit = 0
for i in range(len(df3[series1])):
    if corr > 0.7:
        if df3['ratio'][i] < (mean_ratio - sd):
            if position == 0:
                buy1 = df3[series1][i]
                sell2 = df3[series2][i]
                print(df3.index[i], "Buy", df3[series1][i], "Sell", df3[series2][i])
                position = 1
            elif position == -1:
                profit = (sell1 - df3[series1][i]) + (df3[series2][i] - buy2)
                cum_profit = cum_profit + profit
                print(df3.index[i], "Sell Exit", df3[series1][i], "Buy Exit", df3[series2][i], "Profit", cum_profit)
                position = 0
            else:
                continue
        elif df3['ratio'][i] > (mean_ratio + sd):

            if position == 0:
                print(df3.index[i], "Sell", df3[series1][i], "Buy", df3[series2][i])
                sell1 = df3[series1][i]
                buy2 = df3[series2][i]
                position = -1
            elif position == 1:
                profit = (df3[series1][i] - buy1) + (sell2 - df3[series2][i])
                cum_profit = cum_profit + profit
                print(df3.index[i], "Buy Exit", df3[series1][i], " Sell Exit", df3[series2][i], "Profit", cum_profit)
                position = 0
            else:
                continue
    else:
        print('no corr')

# output to a csv
df3.to_csv('/Users/shayakroy/Desktop/Trading Videos/Pyhton/Pair Trading/Pair_ratios.csv')
