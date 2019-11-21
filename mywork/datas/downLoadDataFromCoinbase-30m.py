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
    f=open(tradePair + "-" + str(minTime) + 'm-coinbase.txt','a')    # r只读，w可写，a追加
    f.write('Date,Open,High,Low,Close,Volume,OpenInterest,iniTimestamp\n')
    for item_str in reversed(data_arr):
        item = item_str.split(",")
        candleTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(item[0])))
        f.write(str(candleTime)+","+str(item[3])+","+str(item[2])+","+str(item[1])+","+str(item[4])+","+str(item[5])+",0,"+str(item[0])+'\n')
    f.close()

if __name__ == '__main__':
    beginTime = datetime(2016,6,17,0,0,0,0)
    delta = 300
    minTime = 5
    test = beginTime - timedelta(minutes=delta*minTime)
    print(test)
    tmp_time_array = create_time_array(beginTime,delta,minTime)
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
        print("begin sleep！")
        time.sleep(15)

    # data_str = "[[1571877900,7464.35,7472,7464.76,7471.57,18.14071708],[1571877600,7456.59,7469.08,7467.91,7464.84,27.95408492]]"
    # print(type(data_str))
    # print(data_str.isdigit())
    # data_str2 = data_str.replace("[[",'').replace("]]",'').split("],[")
    # print(type(data_str2))

