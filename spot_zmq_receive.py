#-*-coding:utf-8-*- 3
import json
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE,b'')
#socket.connect("tcp://192.168.1.211:20064")
socket.connect("tcp://192.168.1.216:20061")

while True:
    # 快照
    revjson = json.loads( socket.recv() )
    print(revjson)
    if revjson['message_type']==4:
        if revjson['contract_id']==10:
            print(time.time())
            print(revjson)
    #逐笔成交
    if revjson['message_type']==6:
        if revjson['contract_id']==10:
            print(time.time())
            print(revjson)

    # k线
    if revjson['message_type']==7:
        if revjson['contract_id']==10:
            print(time.time())
            print(revjson)
