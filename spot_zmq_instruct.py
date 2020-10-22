import json
import time

import zmq

from util import operSql


def getBigNumber(number):
    return str(int(number * 1000000000000000000))

def to_decimal(f, p = 10):
    i = round(f * pow(10, p))                 #pow(10,i)的意思就是10的i次幂，round() 方法返回浮点数x的四舍五入值
    return str(round(i * pow(10, 18 - p)))


# 定义装饰器
def zmq_wapper(func):
    def wrapper(*args, **kargs):
        TRADE_SERVER_URL = 'tcp://192.168.1.216:20060'
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.connect(TRADE_SERVER_URL)
        f = func(*args,**kargs)
        str_json = json.dumps(f).encode('utf-8')
        #print(str_json)
        socket.send(str_json)
        #time.sleep(1)
        ret = json.loads(socket.recv())
        print(ret)
        # if ret['code']!=0:
        #     print(ret)
        return ret
    return wrapper

#交易对挂牌
@zmq_wapper
def contractPutup(contract_id,type=2):
    #获取交易对数据
    contractsql=('SELECT * FROM core_contract  WHERE contract_id=%d'%(contract_id))
    contract = operSql(contractsql,'MysqlSpot',1)
    print(contract)
    datajson={}
    datajson['message_type'] = 5007
    datajson['appl_id'] = 1
    datajson['contract_id'] = contract['contract_id']
    datajson['symbol'] = contract['symbol']
    #datajson['symbol'] = 'BTC/USDT'
    datajson['price_tick'] = to_decimal(contract['price_tick'])
    datajson['lot_size'] = to_decimal(contract['lot_size'])
    datajson['taker_fee_ratio'] = to_decimal(contract['taker_fee_ratio'])
    datajson['maker_fee_ratio'] = to_decimal(contract['maker_fee_ratio'])
    datajson['limit_max_level'] = contract['limit_max_level']
    datajson['market_max_level'] = contract['market_max_level']
    datajson['price_limit_rate'] = to_decimal(contract['price_limit_rate'])
    #datajson['max_num_orders'] = 10
    datajson['commodity_id'] = contract['commodity_id']
    datajson['currency_id'] = contract['currency_id']
    #datajson['contract_status'] = contract['contract_status'] # 1-集合竞价，2-连续竞价，3-交易暂停，4-已摘牌
    datajson['contract_status'] = 2
    datajson['list_time'] = contract['list_time']
    # datajson['min_order_amt'] = contract['min_order_amt']
    datajson['list_price'] = to_decimal(contract['list_price'])
    datajson['type'] = type # 1-新增，2-更新，3-删除
    return datajson
#contractPutup(1,1)


#交易对摘牌
@zmq_wapper
def contractDelist(contract_id):
    datajson={}
    datajson['message_type'] = 5007
    datajson['appl_id'] = 1
    datajson['type'] = 3
    datajson['contract_id'] = contract_id
    datajson['contract_status'] = 4
    return datajson
#contractDelist(1)
#重新加载交易参数质量


#账号交易参数更新 dui
# def core_marginRefresh():
#     datajson={}
#     datajson['message_type'] = 5004
#     datajson['appl_id'] = 1
#     datajson['contract_id'] = 1
#     datajson['account_id'] = 12
#     datajson['type'] = 0
#     datajson['forbid_trade'] = 0
#     datajson['taker_fee_ratio'] = 12
#     datajson['make_fee_ratio'] = 0
#     return datajson

#一键更新core_param core_group_param core_param_orders 5009
@zmq_wapper
def paramRefresh5009():
    datajson={}
    datajson['message_type'] = 5009
    datajson['appl_id'] = 1
    return datajson
#paramRefresh5009()

#一键更新core_group_param 5015
@zmq_wapper
def paramRefresh5015(type,conrtact_id,group_id,account_id):
    datajson={}
    datajson['message_type'] = 5015
    datajson['appl_id'] = 1
    datajson['type'] = type #1新增2修改3删除
    datajson['variety_id'] = 0 #现货为0
    datajson['conrtact_id'] = conrtact_id
    datajson['group_id'] = group_id
    datajson['account_id'] = account_id
    return datajson


#限价主动委托
@zmq_wapper
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
# paramRefresh5015(2,1,2,666666)
# paramRefresh5009()
#ret = limitOrderPlace(1,100003,1,1,1)
#print(ret)

#市价主动委托
@zmq_wapper
def marketOrderPlace(contract_id,account_id,side,quantity):
    datajson={}
    datajson['message_type'] = 1001
    datajson['appl_id'] = 1
    datajson['contract_id'] = contract_id
    datajson['account_id'] = account_id
    datajson['client_order_id'] = str(int(time.time() * 1000000))
    datajson['side'] = side
    #datajson['price'] = to_decimal(price)
    datajson['quantity'] = to_decimal(quantity)
    datajson['order_type'] = 3
    # datajson['order_sub_type'] = 0
    datajson['time_in_force'] = 1
    # datajson['stop_condition'] = ""
    # datajson['stop_price'] = ""
    # datajson['minimal_quantity'] = ""
    # datajson['disclose_quantity'] = ""
    return datajson
#marketOrderPlace(1,666666,1,1)

#撤单
@zmq_wapper
def orderCancel(account_id,contract_id,cl_order_id):
    datajson={}
    datajson['message_type'] = 1003
    datajson['appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['contract_id'] = contract_id
    datajson['original_order_id'] = cl_order_id
    datajson['cl_order_id'] = str(int(time.time() * 1000000))
    return datajson
#orderCancel(666666,1,"11600758357211715")

#一键撤单
@zmq_wapper
def orderAllCancel(account_id,contract_id=0):
    datajson={}
    datajson['message_type'] = 1008
    datajson['appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['contract_id'] = contract_id #=0所有交易对委托全部撤单，非0只撤指定交易对
    datajson['currency_id'] = 0
    datajson['cl_order_id'] = str(int(time.time() * 1000000))
    return datajson
#orderAllCancel(0,1)

#批量撤单
#contract_id0  original_order_id1 client_order_id2
@zmq_wapper
def orderBatchCancel(account_id,cancels):
    datajson={}
    datajson['message_type'] = 1031
    datajson['appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['client_order_id'] = str(int(time.time() * 1000000))
    cancelList=[]
    for cancel in cancels:
        c={}
        c['contract_id'] = cancel[0]
        c['original_order_id'] = cancel[1]
        c['client_order_id'] = str(cancel[2])
        cancelList.append(c)
    datajson['cancels'] = cancelList
    return datajson
#orderBatchCancel(666666,[{"contract_id":1,"original_order_id":"11600758357211719","client_order_id":"1"},{"contract_id":1,"original_order_id":"116007583572117100","client_order_id":"2"}])

#批量转账 0 account_id 1 currency_id  2 from_appl_id 3 to_appl_id 4 quantity
@zmq_wapper
def transferBatch(transfers):
    datajson={}
    datajson['message_type'] = 4006
    datajson['appl_id'] = 1
    tlist=[]
    for transfer in transfers:
        t={}
        t['account_id'] = transfer[0]
        t['currency_id'] = transfer[1]
        t['from_appl_id'] = transfer[2]
        t['to_appl_id'] = transfer[3]
        t['quantity'] = to_decimal(transfer[4])
        t['id'] = str(int(time.time() * 1000000))
        t['batch_id'] = str(1)
        tlist.append(t)
    datajson['transfers'] = tlist
    return datajson
#transferBatch([{"account_id":666666,"from_appl_id":7,"to_appl_id":1,"currency_id":4,"quantity":getBigNumber(1),"id":str(int(time.time() * 1000000)),"batch_id":"1"},
#               {"account_id":666667,"from_appl_id":7,"to_appl_id":1,"currency_id":3,"quantity":getBigNumber(1),"id":str(int(time.time() * 1000000)),"batch_id":"1"}])

#批量下单
@zmq_wapper
def orderPlaceBatch(account_id,orders):
    print(1)
    datajson = {}
    datajson['message_type'] = 1009
    datajson['appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['client_order_id'] = str(int(time.time() * 1000000))
    orderslist=[]
    #contract_id,order_type,side,order_price,order_qty,client_order_id
    for order in orders:
        o={}
        o['contract_id']=order[0]
        o['order_type'] = order[1]
        o['side'] = order[2]
        o['order_price'] = to_decimal(order[3])
        o['order_qty'] = to_decimal(order[4])
        o['client_order_id'] = str(order[5])
        orderslist.append(o)
    datajson['orders'] = orderslist
    #print(datajson)
    return datajson
#contract = [{"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1100000000000000000", "order_qty": "2100000000000000000", "client_order_id": "1001"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1200000000000000000", "order_qty": "2200000000000000000", "client_order_id": "1002"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1300000000000000000", "order_qty": "2300000000000000000", "client_order_id": "1003"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1400000000000000000", "order_qty": "2400000000000000000", "client_order_id": "1004"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1500000000000000000", "order_qty": "2500000000000000000", "client_order_id": "1005"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1600000000000000000", "order_qty": "2600000000000000000", "client_order_id": "1006"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1700000000000000000", "order_qty": "2700000000000000000", "client_order_id": "1007"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1800000000000000000", "order_qty": "2800000000000000000", "client_order_id": "1008"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "1900000000000000000", "order_qty": "2900000000000000000", "client_order_id": "1009"}, {"contract_id": 1, "order_type": 1, "side": 1, "order_price": "2000000000000000000", "order_qty": "3000000000000000000", "client_order_id": "1010"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4100000000000000000", "order_qty": "5100000000000000000", "client_order_id": "2001"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4200000000000000000", "order_qty": "5200000000000000000", "client_order_id": "2002"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4300000000000000000", "order_qty": "5300000000000000000", "client_order_id": "2003"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4400000000000000000", "order_qty": "5400000000000000000", "client_order_id": "2004"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4500000000000000000", "order_qty": "5500000000000000000", "client_order_id": "2005"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4600000000000000000", "order_qty": "5600000000000000000", "client_order_id": "2006"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4700000000000000000", "order_qty": "5700000000000000000", "client_order_id": "2007"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4800000000000000000", "order_qty": "5800000000000000000", "client_order_id": "2008"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "4900000000000000000", "order_qty": "5900000000000000000", "client_order_id": "2009"}, {"contract_id": 1, "order_type": 1, "side": -1, "order_price": "5000000000000000000", "order_qty": "6000000000000000000", "client_order_id": "2010"}]
# for i in range(1,201):
#     orders = [[i, 1, 1, 1.1, 2.1, 1001],
#               [i, 1, 1, 1.2, 2.2, 1002],
#               [i, 1, 1, 1.3, 2.3, 1003],
#               [i, 1, 1, 1.4, 2.4, 1004],
#               [i, 1, 1, 1.5, 2.5, 1005],
#               [i, 1, 1, 1.6, 2.6, 1006],
#               [i, 1, 1, 1.7, 2.7, 1007],
#               [i, 1, 1, 1.8, 2.8, 1008],
#               [i, 1, 1, 1.9, 2.9, 1009],
#               [i, 1, 1, 2.0, 3.0, 1010],
#               [i, 1, 1, 2.1, 2.1, 1001],
#               [i, 1, 1, 2.2, 2.2, 1002],
#               [i, 1, 1, 2.3, 2.3, 1003],
#               [i, 1, 1, 2.4, 2.4, 1004],
#               [i, 1, 1, 2.5, 2.5, 1005],
#               [i, 1, 1, 2.6, 2.6, 1006],
#               [i, 1, 1, 2.7, 2.7, 1007],
#               [i, 1, 1, 2.8, 2.8, 1008],
#               [i, 1, 1, 2.9, 2.9, 1009],
#               [i, 1, 1, 3.0, 3.0, 1010],
#               [i, 1, 1, 3.1, 2.1, 1001],
#               [i, 1, 1, 3.2, 2.2, 1002],
#               [i, 1, 1, 3.3, 2.3, 1003],
#               [i, 1, 1, 3.4, 2.4, 1004],
#               [i, 1, 1, 3.5, 2.5, 1005],
#               [i, 1, 1, 3.6, 2.6, 1006],
#               [i, 1, 1, 3.7, 2.7, 1007],
#               [i, 1, 1, 3.8, 2.8, 1008],
#               [i, 1, 1, 3.9, 2.9, 1009],
#               [i, 1, 1, 4.0, 3.0, 1010],
#               [i, 1, -1, 4.1, 5.1, 2001],
#               [i, 1, -1, 4.2, 5.2, 2002],
#               [i, 1, -1, 4.3, 5.3, 2003],
#               [i, 1, -1, 4.4, 5.4, 2004],
#               [i, 1, -1, 4.5, 5.5, 2005],
#               [i, 1, -1, 4.6, 5.6, 2006],
#               [i, 1, -1, 4.7, 5.7, 2007],
#               [i, 1, -1, 4.8, 5.8, 2008],
#               [i, 1, -1, 4.9, 5.9, 2009],
#               [i, 1, -1, 5.0, 6.0, 2010],
#               [i, 1, -1, 5.1, 5.1, 2001],
#               [i, 1, -1, 5.2, 5.2, 2002],
#               [i, 1, -1, 5.3, 5.3, 2003],
#               [i, 1, -1, 5.4, 5.4, 2004],
#               [i, 1, -1, 5.5, 5.5, 2005],
#               [i, 1, -1, 5.6, 5.6, 2006],
#               [i, 1, -1, 5.7, 5.7, 2007],
#               [i, 1, -1, 5.8, 5.8, 2008],
#               [i, 1, -1, 5.9, 5.9, 2009],
#               [i, 1, -1, 6.0, 6.0, 2010],
#               [i, 1, -1, 6.1, 5.1, 2001],
#               [i, 1, -1, 6.2, 5.2, 2002],
#               [i, 1, -1, 6.3, 5.3, 2003],
#               [i, 1, -1, 6.4, 5.4, 2004],
#               [i, 1, -1, 6.5, 5.5, 2005],
#               [i, 1, -1, 6.6, 5.6, 2006],
#               [i, 1, -1, 6.7, 5.7, 2007],
#               [i, 1, -1, 6.8, 5.8, 2008],
#               [i, 1, -1, 6.9, 5.9, 2009],
#               [i, 1, -1, 7.0, 6.0, 2010],
#               ]
#     orderPlaceBatch(100000+i,orders )
    #time.sleep(10)

# orderAllCancel(666666, 0)



#更新用户分组信息
@zmq_wapper
def userGroupRefresh(account_id,contract_id,type):
    datajson = {}
    datajson['message_type'] = 5015
    datajson['appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['variety_id'] =0
    datajson['contract_id'] =contract_id
    datajson['type'] = type #1新增2修改3删除
    return datajson
#userGroupRefresh(666666,1,3)
#更新core_marketmaker
@zmq_wapper
def marketmakerRefresh():
    datajson = {}
    datajson['message_type'] = 5018
    datajson['appl_id'] = 1
    return datajson
#marketmakerRefresh()
@zmq_wapper
def loginRefresh(account_id,type):
    datajson = {}
    datajson['message_type'] = 1029
    datajson['appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['type'] = type
    return datajson
#loginRefresh(0,0)
#现货账号加钱
@zmq_wapper
def spotAddMoney(account_id,currency_id,quantity):
    datajson={}
    datajson['message_type'] = 4005
    datajson['from_appl_id'] = 5
    datajson['to_appl_id'] = 1
    datajson['account_id'] = account_id
    datajson['currency_id'] = currency_id
    datajson['id'] = str(int(time.time() * 1000000))
    datajson['quantity'] = to_decimal(quantity)
    return datajson
# for i in range(1,201):
#     cSql = 'select * from core_contract where contract_id=%s ' % (i)
#     result = operSql(cSql, 'MysqlSpot', 1)
#     spotAddMoney(100000+i, result['commodity_id'], 10000000)
#     spotAddMoney(100000 + i, result['currency_id'], 10000000)

#spotAddMoney(666667,2,10000)

#现货账号减钱
@zmq_wapper
def spotminusMoney(account_id,currency_id,quantity):
    datajson={}
    datajson['message_type'] = 4005
    datajson['from_appl_id'] = 1
    datajson['to_appl_id'] = 5
    datajson['account_id'] = account_id
    datajson['currency_id'] = currency_id
    datajson['id'] = str(int(time.time() * 1000000))
    datajson['quantity'] = to_decimal(quantity)
    return datajson

# ret = paramRefresh5015(2, 2, 3, 666666)
# print(ret)
# paramRefresh5009()
# ret = limitOrderPlace(1, 666666, 1, 1, 1)
# ret = limitOrderPlace(1, 666666, -1, 1, 1)
# print(ret)



# if __name__ == '__main__':
#     TRADE_SERVER_URL = 'tcp://192.168.1.216:20050'
#     context = zmq.Context()
#     socket = context.socket(zmq.DEALER)
#     socket.connect(TRADE_SERVER_URL)
#     datajson = paramRefresh5009()
#     str_json = json.dumps(datajson).encode('utf-8')
#     print(str_json)
#     socket.send(str_json)
#     ret = socket.recv()
#     print(ret)

