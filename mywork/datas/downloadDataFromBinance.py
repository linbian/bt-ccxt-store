

from datetime import datetime, timedelta
import time
import requests
import csv


def get_url(beginTime,interval,tradePair):
    url = "https://www.binancezh.com/api/v3/klines?symbol={}&interval={}&startTime={}&limit=1000".format(tradePair,interval,beginTime)
    # url = "https://www.binancezh.com/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime=1499040000000&limit=1000".format(tradePair,)
    return url

def get_data(url,interval,tradePair):
    response = requests.get(url)
    data_arr = response.text.replace("[[",'').replace("]]",'').split("],[")
    f=open(tradePair + "-" + str(interval) + '-binance.txt','a')    # r只读，w可写，a追加
    f.write('Date,Open,High,Low,Close,Volume,Amount,TradeTicks,beginTimestamp,endTimestamp\n')
    endTimestamp = 0
    for item_str in data_arr:
        item = item_str.replace("\"",'').split(",")
        candleTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(item[0])/1000))
        f.write(str(candleTime)+","+str(item[1])+","+str(item[2])+","+str(item[3])+","+str(item[4])+","+str(item[5])+","+str(item[7])+","+str(item[8])+","+str(item[0])+","+str(item[6])+'\n')
        endTimestamp=item[6]
    f.close()
    return int(endTimestamp)

if __name__ == '__main__':
    tradePair = "BTCUSDT"
    interval = "5m"
    beginTime = 1502942400000 #2017-08-17 12:00:00
    # beginTime = 1573531200000
    endTime = beginTime
    # url = get_url(beginTime,interval,tradePair)
    # endTimeStamp = get_data(url,interval,tradePair)
    # print(endTimeStamp)
    count = 1
    while endTime>0:
        url = get_url(endTime,interval,tradePair)
        print(url, " <=== " ,count)
        endTimeStamp = get_data(url,interval,tradePair)
        if endTimeStamp > 0:
            endTime = endTimeStamp + 1
        else:
            endTime = 0
        count += 1
        print("begin sleep！")
        time.sleep(3)


