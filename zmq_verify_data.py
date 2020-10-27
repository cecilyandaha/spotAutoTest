import random
import time

from zmq_spot_instruct import orderPlaceBatch, spotAddMoney, orderAllCancel, orderCancel
from util import operSql



# 给所有已有账号随机币种划转
def batch_transfer_account():
    cSql = 'select * from core_account '
    results = operSql(cSql, 'MysqlSpot')
    for result in results :
        spotAddMoney(result['user_id'], random.randint(1,200), random.randrange(100000,10000000))

#batch_transfer_account()
#batch_transfer_currency()



def data_check(type,data1,data2,user_id=0,currency_id=0):
    data1 = round(float(data1), 8)
    data2 = round(float(data2), 8)
    if currency_id >0:
        if data1 != data2:
            print('%s 用户%s 币种 %s 核对数据不正确  data1=%s data2=%s' % (type,user_id, currency_id, data1, data2))
            # print(data2-data1)
        # if data1==data2:
        #     print('用户%s 币种 %s 核对数据正确  数据库=%s 计算值=%s' %(user_id,currency_id,data1,data2))
    if currency_id == 0 and user_id==0:
        if data1 != data2:
            print('%s 数值1：%s 数值2：%s' % (type,data1, data2))



# 单个total_money用户对账
def verify_total_money(user_id,currency_id,total_money):

    # 通过currency_id 找这个人在对应的交易对的core_match数据 core_transfer数据 以及未成交的core_order数据
    account = 0
    cSql = 'select contract_id from core_contract where currency_id=%s ' % (currency_id)
    contracts = operSql(cSql, 'MysqlSpot')
    for contract in contracts:
        id = contract['contract_id']
        cSql = 'SELECT ((CASE WHEN m.ask IS NULL  THEN 0 ELSE m.ask END) - (CASE WHEN m.bid IS NULL  THEN 0 ELSE m.bid END )) amt ' \
               'FROM (SELECT  (SELECT sum( match_amt )- sum( ask_fee ) FROM core_match WHERE ask_user_id =%s AND contract_id=%s ) ask,' \
               '(SELECT sum( match_amt) + sum(bid_fee ) FROM core_match WHERE bid_user_id = %s AND contract_id=%s ) bid FROM DUAL) m' % (
               user_id, id, user_id, id)
        r = operSql(cSql, 'MysqlSpot', 1)
        account += r['amt']
    cSql = 'select contract_id from core_contract where commodity_id=%s ' % (currency_id)
    contracts = operSql(cSql, 'MysqlSpot')
    for contract in contracts:
        id = contract['contract_id']
        cSql = 'SELECT ((CASE WHEN m.bid IS NULL  THEN 0 ELSE m.bid END) - (CASE WHEN m.ask IS NULL  THEN 0 ELSE m.ask END )) qty ' \
               'FROM (SELECT  (SELECT sum( match_qty ) FROM core_match WHERE ask_user_id =%s AND contract_id=%s ) ask,' \
               '(SELECT sum(match_qty) FROM core_match WHERE bid_user_id = %s AND contract_id=%s ) bid FROM DUAL) m' % (
               user_id, id, user_id, id)
        r = operSql(cSql, 'MysqlSpot', 1)
        account += r['qty']
    cSql = 'SELECT ((CASE WHEN m.a IS NULL  THEN 0 ELSE m.a END) - (CASE WHEN m.s IS NULL  THEN 0 ELSE m.s END )) transfer ' \
           'FROM (SELECT (SELECT sum( quantity )  FROM core_transfer WHERE user_id = %s AND currency_id=%s AND to_appl_id=1) a ,' \
           '(SELECT sum( quantity ) FROM core_transfer WHERE user_id =%s AND currency_id=%s AND from_appl_id=1) s FROM DUAL) m' % (
           user_id, currency_id, user_id, currency_id)
    r = operSql(cSql, 'MysqlSpot', 1)
    account += r['transfer']
    data_check('单个total_money用户对账',total_money, account, user_id, currency_id)

# 单个用户order_frozen_money对账
def verify_order_frozen_money(user_id):
    # 拼接查询的订单库
    tablename = 'core_order_%s' %(user_id%10)
    cSql = 'SELECT o.price,o.quantity,o.filled_currency,o.filled_quantity,o.maker_fee_ratio,o.side,c.commodity_id,c.currency_id FROM %s o,core_contract c ' \
           'WHERE o.contract_id=c.contract_id AND o.user_id=%s AND o.order_status IN (2,3)' % (tablename,user_id)
    orders = operSql(cSql, 'MysqlSpot')
    accounts={}
    for order in orders:
        if order['side']==1:
            if order['currency_id']  in accounts:
                accounts[order['currency_id']]+=((order['quantity']-order['filled_quantity'])*order['price'])*(1+order['maker_fee_ratio'])
            else:
                accounts[order['currency_id']] =((order['quantity']-order['filled_quantity'])*order['price'])*(1+order['maker_fee_ratio'])
        elif order['side']==-1:
            if order['commodity_id']  in accounts:
                accounts[order['commodity_id']]+=order['quantity']-order['filled_quantity']
            else:
                accounts[order['commodity_id']] =order['quantity']-order['filled_quantity']
    for key in accounts:
        cSql = 'select order_frozen_money from core_account where user_id=%s and currency_id=%s ' % (user_id,key)
        contracts = operSql(cSql, 'MysqlSpot',1)
        data_check('单个用户order_frozen_money对账',contracts['order_frozen_money'],accounts[key],user_id,key)


# 单个用户core_user_fee_stat对账
def very_core_user_fee_stat(user_id,contract_id):
    cSql = 'SELECT (CASE WHEN m.ad IS NULL  THEN 0 ELSE m.ad END) fee FROM (SELECT ' \
           '(SELECT SUM(stat_fee)  FROM core_user_fee_stat WHERE user_id=%s AND contract_id=%s) ad FROM DUAL ) m' %(user_id,contract_id)
    result1 = operSql(cSql, 'MysqlSpot',1)
    cSql = 'SELECT ((CASE WHEN m.ad IS NULL  THEN 0 ELSE m.ad END) + (CASE WHEN m.su IS NULL  THEN 0 ELSE m.su END ))fee FROM' \
           '(SELECT (SELECT SUM(bid_fee) FROM core_match WHERE bid_user_id=%s AND contract_id=%s) ad ,' \
           '(SELECT SUM(ask_fee) FROM core_match WHERE ask_user_id=%s AND contract_id=%s) su FROM DUAL)m ' %(user_id,contract_id,user_id,contract_id)
    result2 = operSql(cSql, 'MysqlSpot',1)
    data_check('单个用户core_user_fee_stat对账', result1['fee'], result2['fee'], user_id, contract_id)


def very_core_user_fee_stats():
    cSql =  'SELECT DISTINCT user_id,contract_id  from core_user_fee_stat'
    results = operSql(cSql, 'MysqlSpot')
    for result in results:
        very_core_user_fee_stat(result['user_id'], result['contract_id'])

#very_core_user_fee_stats()

# 总体对账
def very_total():
    #total_money 总体对账
    cSql = 'SELECT ((CASE WHEN m.ad IS NULL  THEN 0 ELSE m.ad END) - (CASE WHEN m.su IS NULL  THEN 0 ELSE m.su END )-' \
           '(CASE WHEN m.fee IS NULL  THEN 0 ELSE m.fee END )) transfer ' \
           'FROM (SELECT (SELECT SUM(quantity) FROM core_transfer WHERE to_appl_id=1) ad,' \
           '(SELECT SUM(quantity) FROM core_transfer WHERE from_appl_id=1) su,' \
           '(SELECT SUM(stat_fee) FROM core_user_fee_stat) as fee FROM DUAL) m'
    transfer = operSql(cSql, 'MysqlSpot', 1)
    cSql = 'SELECT SUM(total_money) as total_money FROM core_account '
    account = operSql(cSql, 'MysqlSpot', 1)
    data_check('total_money 总体对账',transfer['transfer'], account['total_money'])

    #手续费总体对账
    cSql = 'SELECT SUM(bid_fee+ask_fee) as fee FROM core_match'
    fee1 = operSql(cSql, 'MysqlSpot',1)
    cSql = 'SELECT SUM(stat_fee) as fee FROM core_user_fee_stat;'
    fee2 = operSql(cSql, 'MysqlSpot',1)
    cSql = 'SELECT SUM(stat_real_fee) as fee FROM core_user_fee_stat;'
    fee3 = operSql(cSql, 'MysqlSpot',1)
    match_fee=fee1['fee']
    stat_fee=fee2['fee']
    stat_real_fee=fee3['fee']
    data_check('core_match手续费总和与stat_fee总和比对',match_fee,stat_fee)
    data_check('core_match手续费总和与stat_real_fee总和比对',match_fee, stat_real_fee)


def verify_total_moneys():
    # 查询出所有账号 循环对账
    cSql = 'select * from core_account '
    results = operSql(cSql, 'MysqlSpot' )
    for result in results:
        currency_id = result['currency_id']
        user_id = result['user_id']
        total_money = result['total_money']
        verify_total_money(user_id,currency_id,total_money)

def verify_order_frozen_moneys():
    cSql = 'select DISTINCT user_id from core_account '
    results = operSql(cSql, 'MysqlSpot' )
    for result in results:
        user_id = result['user_id']
        verify_order_frozen_money(user_id)


# 批量对账
def verify_accounts():
    #very_total()
    verify_total_moneys()
    #verify_order_frozen_moneys()
    #very_core_user_fee_stats


verify_accounts()



# cancelAllUsersOrders()

#orderCancel(100004,77,"11603097733011094")
#time.sleep(2)
#verify_order_frozen_money(100004)
#verify_accounts()


















#orderAllCancel(100010,0)
#produce_order(10,11)
