import datetime
import json
import random
import threading
import time

import zmq

def to_decimal(f, p = 10):
    i = round(f * pow(10, p))                 #pow(10,i)的意思就是10的i次幂，round() 方法返回浮点数x的四舍五入值
    return str(round(i * pow(10, 18 - p)))

def limitOrderPlace(contract_id,account_id,side,price,quantity):
    datajson={}
    datajson['message_type'] = 1001
    datajson['appl_id'] = 1
    datajson['contract_id'] = contract_id
    datajson['account_id'] = account_id
    datajson['client_order_id'] = str(int(time.time() * 1000000))
    datajson['side'] = side
    datajson['price'] = to_decimal(price)
    datajson['quantity'] = to_decimal(quantity)
    datajson['order_type'] = 1
    # datajson['order_sub_type'] = 0
    datajson['time_in_force'] = 1
    # datajson['stop_condition'] = ""
    # datajson['stop_price'] = ""
    # datajson['minimal_quantity'] = ""
    # datajson['disclose_quantity'] = ""
    #print(datajson)
    return datajson

def order(pare):
    TRADE_SERVER_URL = 'tcp://192.168.1.216:20060'
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(TRADE_SERVER_URL)
    # f = limitOrderPlace(pare, 100000+pare, 1, 10, 1)
    # str_json1 = json.dumps(f).encode('utf-8')
    # f = limitOrderPlace(pare, 100000+pare, -1, 10, 1)
    # str_json2 = json.dumps(f).encode('utf-8')

    #start_time = datetime.datetime.now()
    #for i in range(0,1000):
    while True:
        ran = random.randint(0, 9)
        f = limitOrderPlace(pare, 100000 + pare, 1, 10 + ran, 1)
        str_json1 = json.dumps(f).encode('utf-8')
        #ran = random.randint(0, 9)
        f = limitOrderPlace(pare, 100000 + pare, -1, 10 + ran, 1)
        str_json2 = json.dumps(f).encode('utf-8')

        socket.send(str_json1)
        ret = json.loads(socket.recv())
        print(ret)
        socket.send(str_json2)
        ret = json.loads(socket.recv())

        #socket.send(str_json2)
        #ret = json.loads(socket.recv())
        print(ret)
        time.sleep(5)
    #end_time = datetime.datetime.now()
    #print(1000 / (end_time - start_time).total_seconds())


Threads=[]
T1=threading.Thread(target=order,args=(10,))
#T2=threading.Thread(target=order,args=(11,))
# T3=threading.Thread(target=order,args=(12,))
# T4=threading.Thread(target=order,args=(13,))
# T5=threading.Thread(target=order,args=(14,))
# T6=threading.Thread(target=order,args=(15,))
# T7=threading.Thread(target=order,args=(16,))
# T8=threading.Thread(target=order,args=(17,))
# T9=threading.Thread(target=order,args=(18,))
# T10=threading.Thread(target=order,args=(19,))
Threads.append(T1)
#Threads.append(T2)
# Threads.append(T3)
# Threads.append(T4)
# Threads.append(T5)
# Threads.append(T6)
# Threads.append(T7)
# Threads.append(T8)
# Threads.append(T9)
# Threads.append(T10)

if __name__ =='__main__':
    for t in Threads:
        # t.setDaemon(True)
        t.start()



