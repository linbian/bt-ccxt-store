from datetime import datetime, timedelta
import time
import requests
import csv

def create_time_array(beginTime,delta,minTime):
    endTime = beginTime + timedelta(minutes=delta*minTime)
    time_array = []
    time_array.append([beginTime,endTime])
    return time_array

def get_url(beginTime,endTime,minTime,tradePair):
    granularity = 60 * minTime
    start = beginTime.strftime("%Y-%m-%d %H:%M:%S")
    end = endTime.strftime("%Y-%m-%d %H:%M:%S")
    url = "https://api.pro.coinbase.com/products/{}/candles?granularity={}&start={}&end={}".format(tradePair,granularity,start,end)
    return url

def get_data(url):
    response = requests.get(url)
    data_arr = response.text.replace("[[",'').replace("]]",'').split("],[")

    for item_str in reversed(data_arr):
        item = item_str.split(",")
        candleTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(item[0])))
        print(str(candleTime)+","+str(item[3])+","+str(item[2])+","+str(item[1])+","+str(item[4])+","+str(item[5])+",0,"+str(item[0]))

def reload(beginTime):
    delta = 300
    minTime = 60
    test = beginTime - timedelta(minutes=delta*minTime)
    # print(test)
    tmp_time_array = create_time_array(test,delta,minTime)
    time_array=[tmp_time_array]
    while (tmp_time_array[-1][1] - datetime.now()).days < 0:
        newBeginTime = tmp_time_array[-1][1]
        if (newBeginTime - datetime.now()).days > 0:
            break
        tmp_time_array = create_time_array(newBeginTime,delta,minTime)
        time_array.append(tmp_time_array)

    count = 1
    for item in time_array:
        tradePair = "BTC-USD"
        url = get_url(item[0][0],item[0][1],minTime,tradePair)
        print(url, " <=== " ,count)
        get_data(url)
        count += 1
        if count == 2:
            break

if __name__ == '__main__':
    reload("2019-10-25 00:00:00")