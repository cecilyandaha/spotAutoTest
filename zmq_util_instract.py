from zmq_spot_instruct import *
from util import *

def cancelAllUsersOrders():
    cSql = 'SELECT user_id FROM core_account WHERE order_frozen_money!=0'
    orders = operSql(cSql, 'MysqlSpot')
    for order in orders:
        orderAllCancel(order['user_id'])


def redisKeyCheck(key,interval):
    before = operateRedis('get',key,'RedisFutureDevelop',db=6)
    flag=0
    while True:
        after = operateRedis('get', key, 'RedisFutureDevelop', db=6)
        time.sleep(interval)
        if before!=after:
            before=after
            print(flag*interval)
        else:
            flag+=1

redisKeyCheck('s_1_206',0.5)




