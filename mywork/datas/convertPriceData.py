from datetime import datetime, timedelta

def convertDateTime(file_name):
    f = open(file_name+".txt")
    line = f.readline()

    ff=open(file_name+"-converted-datetime.txt",'a')    # r只读，w可写，a追加
    ff.write('Date,Time,Open,High,Low,Close,Volume,OpenInterest,iniTimestamp\n')

    count = 0
    while line:
        line = f.readline()  # 继续读取下一行
        # print(line)
        if(line != ''):
            line_array = line.split(",")
            current_datetime = line_array[0]
            current_date = current_datetime.split(" ")[0]
            current_time = current_datetime.split(" ")[1]
            new_line = current_date + "," + current_time + ","
            for i in range(1,6):
                new_line += line_array[i]+ ","
            new_line += line_array[7]
            ff.write(new_line)
    f.close()
    ff.close()

def convertDate(fileName):
    f = open(fileName+".txt")
    line = f.readline()

    ff=open(fileName+"-converted-date.txt",'a')    # r只读，w可写，a追加
    ff.write('Date,Open,High,Low,Close,Volume,OpenInterest,iniTimestamp\n')

    count = 0
    while line:
        line = f.readline()  # 继续读取下一行
        # print(line)
        if(line != ''):
            line_array = line.split(",")
            current_datetime = line_array[0]
            current_date = current_datetime.split(" ")[0]
            new_line = current_date + ","
            for i in range(1,6):
                new_line += line_array[i]+ ","
            new_line += line_array[7]
            ff.write(new_line)
    f.close()
    ff.close()

if __name__ == '__main__':
    # fileName = "BTC-USD-5m-coinbase-old"
    convertDateTime("ETH-USD-5m-coinbase")
    # convertDate("BTC-USD-1D-coinbase")
