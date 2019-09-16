import schedule
import time

import datetime as dt

def job():
    time1 = dt.datetime.now()
    print("I'm not working...", time1)

def job1():
    time1 = dt.datetime.now()
    print("I'm working...", time1)


# schedule.every(1).minutes.do(job)
# schedule.every().minute.at(":4").do(job1)
#schedule.every().minute.at(":50").do(job1)
schedule.every().hour.at(":00").do(job)
schedule.every().hour.at(":05").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)