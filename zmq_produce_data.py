import random
import time

from zmq_util_instract import cancelAllUsersOrders
from zmq_spot_instruct import marketOrderPlace, limitOrderPlace, spotAddMoney, orderPlaceBatch, spotminusMoney
from util import operSql


# 批量生成挂单
def produce_order(a,b):
    for i in range(a,b):
        orders = [[i, 1, 1, 1.1, 2.1, 1001],
                  [i, 1, 1, 1.2, 2.2, 1002],
                  [i, 1, 1, 1.3, 2.3, 1003],
                  [i, 1, 1, 1.4, 2.4, 1004],
                  [i, 1, 1, 1.5, 2.5, 1005],
                  [i, 1, 1, 1.6, 2.6, 1006],
                  [i, 1, 1, 1.7, 2.7, 1007],
                  [i, 1, 1, 1.8, 2.8, 1008],
                  [i, 1, 1, 1.9, 2.9, 1009],
                  [i, 1, 1, 2.0, 3.0, 1010],
                  [i, 1, 1, 2.1, 2.1, 1001],
                  [i, 1, 1, 2.2, 2.2, 1002],
                  [i, 1, 1, 2.3, 2.3, 1003],
                  [i, 1, 1, 2.4, 2.4, 1004],
                  [i, 1, 1, 2.5, 2.5, 1005],
                  [i, 1, 1, 2.6, 2.6, 1006],
                  [i, 1, 1, 2.7, 2.7, 1007],
                  [i, 1, 1, 2.8, 2.8, 1008],
                  [i, 1, 1, 2.9, 2.9, 1009],
                  [i, 1, 1, 3.0, 3.0, 1010],
                  [i, 1, 1, 3.1, 2.1, 1001],
                  [i, 1, 1, 3.2, 2.2, 1002],
                  [i, 1, 1, 3.3, 2.3, 1003],
                  [i, 1, 1, 3.4, 2.4, 1004],
                  [i, 1, 1, 3.5, 2.5, 1005],
                  [i, 1, 1, 3.6, 2.6, 1006],
                  [i, 1, 1, 3.7, 2.7, 1007],
                  [i, 1, 1, 3.8, 2.8, 1008],
                  [i, 1, 1, 3.9, 2.9, 1009],
                  [i, 1, 1, 4.0, 3.0, 1010],
                  [i, 1, -1, 4.1, 5.1, 2001],
                  [i, 1, -1, 4.2, 5.2, 2002],
                  [i, 1, -1, 4.3, 5.3, 2003],
                  [i, 1, -1, 4.4, 5.4, 2004],
                  [i, 1, -1, 4.5, 5.5, 2005],
                  [i, 1, -1, 4.6, 5.6, 2006],
                  [i, 1, -1, 4.7, 5.7, 2007],
                  [i, 1, -1, 4.8, 5.8, 2008],
                  [i, 1, -1, 4.9, 5.9, 2009],
                  [i, 1, -1, 5.0, 6.0, 2010],
                  [i, 1, -1, 5.1, 5.1, 2001],
                  [i, 1, -1, 5.2, 5.2, 2002],
                  [i, 1, -1, 5.3, 5.3, 2003],
                  [i, 1, -1, 5.4, 5.4, 2004],
                  [i, 1, -1, 5.5, 5.5, 2005],
                  [i, 1, -1, 5.6, 5.6, 2006],
                  [i, 1, -1, 5.7, 5.7, 2007],
                  [i, 1, -1, 5.8, 5.8, 2008],
                  [i, 1, -1, 5.9, 5.9, 2009],
                  [i, 1, -1, 6.0, 6.0, 2010],
                  [i, 1, -1, 6.1, 5.1, 2001],
                  [i, 1, -1, 6.2, 5.2, 2002],
                  [i, 1, -1, 6.3, 5.3, 2003],
                  [i, 1, -1, 6.4, 5.4, 2004],
                  [i, 1, -1, 6.5, 5.5, 2005],
                  [i, 1, -1, 6.6, 5.6, 2006],
                  [i, 1, -1, 6.7, 5.7, 2007],
                  [i, 1, -1, 6.8, 5.8, 2008],
                  [i, 1, -1, 6.9, 5.9, 2009],
                  [i, 1, -1, 7.0, 6.0, 2010],
                  ]
        orderPlaceBatch(100000 + i, orders)

# 批量生成账号
def produce_account(a,b):
    for i in range(a,b):
        cSql = 'select * from core_contract where contract_id=%s ' % (i)
        result = operSql(cSql, 'MysqlSpot', 1)
        spotAddMoney(100000 + i, result['commodity_id'], 10000000)
        spotAddMoney(100000 + i, result['currency_id'], 10000000)

# 给所有已有账号已有币种划转
def batch_add_money():
    cSql = 'select * from core_account '
    results = operSql(cSql, 'MysqlSpot')
    for result in results :
        spotAddMoney(result['user_id'], result['currency_id'], random.randrange(100000,10000000))
batch_add_money()
def batch_sub_money():
    cSql = 'select * from core_account '
    results = operSql(cSql, 'MysqlSpot')
    for result in results :
        spotminusMoney(result['user_id'], result['currency_id'], random.randrange(1,10000))

def batch_order():
    cSql = 'select * from core_account '
    results = operSql(cSql, 'MysqlSpot')
    while True:
        for result in results:
            cSql = 'select contract_id from core_contract where currency_id=%s ' % (result['currency_id'])
            contracts = operSql(cSql, 'MysqlSpot')
            for contract in contracts:
                limitOrderPlace(contract['contract_id'],result['user_id'],[-1,1][random.randint(0,1)],round(random.uniform(9,10),random.randint(0,2)),round(random.uniform(0,10000),random.randint(0,4)))
                marketOrderPlace(contract['contract_id'],result['user_id'],[-1,1][random.randint(0,1)],round(random.uniform(0,10000),random.randint(0,4)))
                time.sleep(0.2)

#cancelAllUsersOrders()
#batch_sub_money()
#batch_add_money()
#batch_order()