from datetime import datetime, timedelta
if __name__ == '__main__':
    fileName = "BTC-USD-1D-coinbase.txt"
    seconds_per_min = 60
    minTime = 1440
    f = open(fileName)
    line = f.readline()

    ff=open('new-file.txt','a')    # r只读，w可写，a追加
    ff.write('Date,Open,High,Low,Close,Volume,OpenInterest,iniTimestamp\n')

    line = f.readline()
    last_time = datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S")
    ff.write(line)
    count = 0
    while line:
        line = f.readline()  # 继续读取下一行
        if line == '':
            break
        current_time = datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S")
        # if (current_time-last_time).seconds != seconds_per_min * minTime:
        if (current_time-last_time).seconds != 0 and (current_time-last_time).days != 1:
            count += 1
            if (current_time-last_time).seconds > seconds_per_min * minTime:
                ff.write(line)
            print(current_time,count,(current_time-last_time).days,(current_time-last_time).seconds)
            # print(current_time)
        else:
            ff.write(line)
        last_time = current_time

        # if count > 3:
        #     break
    f.close()
    ff.close()