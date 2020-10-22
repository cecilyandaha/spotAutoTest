from spot_zmq_instruct import *
from util import *

def cancelAllUsersOrders():
    cSql = 'SELECT user_id FROM core_account WHERE order_frozen_money!=0'
    orders = operSql(cSql, 'MysqlSpot')
    for order in orders:
        orderAllCancel(order['user_id'])

