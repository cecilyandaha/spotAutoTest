import unittest

from zmq_util_instract import cancelAllUsersOrders
from zmq_spot_instruct import *

class TestContractParam(unittest.TestCase):
    contract_id=1
    account_id=666666

    @classmethod
    def setUpClass(cls):
        print("this setUpClass() method only called once .\n")
        cSql = ('UPDATE core_contract SET price_limit_rate=100 ,market_max_level=10,limit_max_level=10 ,taker_fee_ratio=0.006,maker_fee_ratio=0.003, contract_status=2 WHERE contract_id=%d' % (
                cls.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        print ("this setupclass() method only called once.\n")
        cSql = 'delete from core_param;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group_param;'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        #恢复core_param_order
        cSql = 'delete from core_param_orders'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, -1, 100, 15);'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, 0, 100, 15);'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        paramRefresh5009()

    @classmethod
    def tearDownClass(cls):
        print ("this teardownclass() method only called once too.\n")

    def setUp(self):
        # 先全部撤单以免下单数量超过限制
        cancelAllUsersOrders()
        print ("do something before test : prepare environment.\n")

    def tearDown(self):

        print ("do something after test : clean up.\n")

    ## 合约上下架 list_time 测试
    def test_contract(self):
        #交易对摘牌
        contractDelist(self.contract_id)

        # 新增合约 合约上市时间大于当前时间
        cSql = ('UPDATE core_contract SET contract_status=%s , list_time=%s WHERE contract_id=%d' % (5,str(round((time.time() + 1000)* 1000000)), self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id,1)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1034, '上市合约大于当前时间合约新增后下单-security not on list yet')

        # 合约上架 合约上市时间大于当前时间
        cSql = ('UPDATE core_contract SET contract_status=%s  WHERE contract_id=%d' % (2, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id, 2)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1034, '上市合约大与当前时间合约上架-security not on list yet')

        #已经存在的合约再次新增
        ret = contractPutup(self.contract_id, 1)
        self.assertEqual(ret['code'], 1027, '已经存在的合约再次新增-list contract has existed')
        # 合约时间修改为当前时间之前 未上市合约下单
        cSql = ('UPDATE core_contract SET contract_status=%s , list_time=%s WHERE contract_id=%d' % (5,str(round((time.time() )* 1000000)), self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id,2)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1011, '新增后下单-symbol forbid trade')
        # 合约时间修改为当前时间之前 合约上架
        cSql = ('UPDATE core_contract SET contract_status=%s  WHERE contract_id=%d' % (2, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id,2)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 0, '上市合约下单成功')

        # 合约交易暂停
        cSql = ('UPDATE core_contract SET contract_status=%s  WHERE contract_id=%d' % (3, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id, 2)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1011, 'symbol forbid trade')
        # 合约摘牌
        cSql = ('UPDATE core_contract SET contract_status=%s  WHERE contract_id=%d' % (4, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractDelist(self.contract_id)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1011, 'symbol forbid trade')
        # 合约恢复上架
        cSql = ('UPDATE core_contract SET contract_status=%s  WHERE contract_id=%d' % (2, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id, 2)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 0, '合约上架-下单正常')

    ## price_tick精度测试
    def test_price_tick(self):
        # 设置合理的合约精度
        price_tick=0.0001
        cSql=('UPDATE core_contract SET price_tick=%s WHERE contract_id=%d'%(price_tick,self.contract_id))
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id,2)
        # 等于合约精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,price_tick, 1)
        self.assertEqual(ret['code'],0,'price_tick正常精度设置-范围精度内下单')
        # 大于合约精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price_tick*0.1, 1)
        self.assertEqual(ret['code'], 1004, 'price_tick超出范围精度内下单-order price invalid')

        # 设置整数精度
        price_tick=1
        cSql=('UPDATE core_contract SET price_tick=%s WHERE contract_id=%d'%(price_tick,self.contract_id))
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id,2)
        # 等于极限精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,price_tick,1)
        self.assertEqual(ret['code'],0,'price_tick整数精度设置-范围精度内下单')
        # 大于极限精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price_tick*0.1,1 )
        self.assertEqual(ret['code'], 1004, 'price_tick超出范围精度内下单-order price invalid')

        # 设置极限合约精度 9位
        price_tick=0.000000001
        cSql=('UPDATE core_contract SET price_tick=%s WHERE contract_id=%d'%(price_tick,self.contract_id))
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id,2)
        # 等于极限精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,price_tick, 1)
        self.assertEqual(ret['code'],0,'price_tick极限精度设置-范围精度内下单')
        # 大于合约精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price_tick*0.1, 1)
        self.assertEqual(ret['code'], 1004, 'price_tick超出范围精度内下单-order price invalid')

    ## lot_size最小交易量测试
    def test_lot_size(self):
        # 设置合理的小数
        lot_size=0.0001
        cSql=('UPDATE core_contract SET lot_size=%s WHERE contract_id=%d'%(lot_size,self.contract_id))
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id)
        # 等于最小交易量
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,1,lot_size)
        self.assertEqual(ret['code'],0,'lot_size最小交易量设置-范围精度内下单')
        # 小于最小交易量
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, lot_size*0.1)
        self.assertEqual(ret['code'], 1005, 'lot_size最小交易量设置-超出范围精度内下单')

        # 设置整数最小交易量
        lot_size=10
        cSql=('UPDATE core_contract SET lot_size=%s WHERE contract_id=%d'%(lot_size,self.contract_id))
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id)
        # 等于最小交易量
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,1,lot_size)
        self.assertEqual(ret['code'],0,'lot_size最小交易量设置-范围精度内下单')
        # 小于最小交易量
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, lot_size*0.1)
        self.assertEqual(ret['code'], 1005, 'lot_size最小交易量设置-超出范围精度内下单')

        # 设置极限最小交易量 9位
        lot_size=0.000000001
        cSql=('UPDATE core_contract SET lot_size=%s WHERE contract_id=%d'%(lot_size,self.contract_id))
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id)
        # 等于极限精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,1,lot_size)
        self.assertEqual(ret['code'],0,'lot_size最小交易量设置-范围精度内下单')
        # 大于合约精度下单
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, lot_size*0.1)
        self.assertEqual(ret['code'], 1005, 'lot_size最小交易量设置-超出范围精度内下单')

    ## taker_fee_ratio/make_fee_ratio taker费率测试
    def test_taker_fee_ratio(self):

        # 设置taker_fee_ratio=0.2，maker_fee_ratio=0.1
        taker_fee_ratio=0.2
        maker_fee_ratio = 0.1
        cSql=('UPDATE core_contract SET taker_fee_ratio=%s, maker_fee_ratio=%s WHERE contract_id=%d'%(taker_fee_ratio,maker_fee_ratio,self.contract_id))
        print(cSql)
        operSql(cSql,'MysqlSpot',1)
        contractPutup(self.contract_id)
        # 用户下单
        price=1
        quality=10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1,price,quality)
        bid_order_id =ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1,price,quality)
        ask_order_id = ret['msg']
        #查询订单
        cSql = ('select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id,ask_order_id))
        result = operSql(cSql, 'MysqlSpot', 1)
        print(result['bid_fee'])
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio),'maker_fee_ratio设置为%s' % (maker_fee_ratio))
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio),'taker_fee_ratio设置为%s' % (taker_fee_ratio))

        # 设置taker_fee_ratio=2，maker_fee_ratio=1
        taker_fee_ratio = 2
        maker_fee_ratio = 1
        cSql = ('UPDATE core_contract SET taker_fee_ratio=%s, maker_fee_ratio=%s WHERE contract_id=%d' % (
        taker_fee_ratio, maker_fee_ratio, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id)
        # 用户下单
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = ('select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id))
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio),'maker_fee_ratio设置为%s' % (maker_fee_ratio))
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio),'taker_fee_ratio设置为%s' % (taker_fee_ratio))

        # 设置taker_fee_ratio=0.002，maker_fee_ratio=0.004
        taker_fee_ratio = 0.002
        maker_fee_ratio = 0.004
        cSql = ('UPDATE core_contract SET taker_fee_ratio=%s, maker_fee_ratio=%s WHERE contract_id=%d' % (
        taker_fee_ratio, maker_fee_ratio, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id)
        # 用户下单
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = ('select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id))
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio),'maker_fee_ratio设置为%s' % (maker_fee_ratio))
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio),'taker_fee_ratio设置为%s' % (taker_fee_ratio))
        orderAllCancel(self.account_id, 0)

    ## limit_max_level 限价最大深度
    def test_limit_max_level(self):

        # 设置限价最大深度为5
        limit_max_level = 5
        cSql = ('UPDATE core_contract SET limit_max_level=%s WHERE contract_id=%d' % (limit_max_level,self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id)
        for i in range(1,limit_max_level+3):
            limitOrderPlace(self.contract_id, self.account_id, -1, i, 1)

        ret = limitOrderPlace(self.contract_id, self.account_id, 1, limit_max_level+1, limit_max_level+1)
        self.assertEqual(ret['code'], 1006,'limit_max_level设置为%s,限价吃单档位数大于限价最大深度相同-order quantity over limit' % (limit_max_level) )

        ret = limitOrderPlace(self.contract_id, self.account_id, 1, limit_max_level, limit_max_level)
        self.assertEqual(ret['code'], 0,'limit_max_level设置为%s,限价吃单档位数与限价最大深度相同' % (limit_max_level) )
        orderAllCancel(self.account_id, 0)

        # 设置限价最大深度为15
        limit_max_level = 15
        cSql = ('UPDATE core_contract SET limit_max_level=%s WHERE contract_id=%d' % (limit_max_level,self.contract_id))
        print(cSql)
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id)
        for i in range(1,limit_max_level+3):
            limitOrderPlace(self.contract_id, self.account_id, -1, i, 1)

        ret = limitOrderPlace(self.contract_id, self.account_id, 1, limit_max_level+1, limit_max_level+1)
        self.assertEqual(ret['code'], 1006,'limit_max_level设置为%s,限价吃单档位数大于限价最大深度相同-order quantity over limit' % (limit_max_level) )

        ret = limitOrderPlace(self.contract_id, self.account_id, 1, limit_max_level, limit_max_level)
        self.assertEqual(ret['code'], 0,'limit_max_level设置为%s,限价吃单档位数与限价最大深度相同' % (limit_max_level) )


    ## market_max_level 市价最大深度
    def test_market_max_level(self):
        #先全部撤单
        orderAllCancel(self.account_id,0)

        # 设置限价最大深度为5
        market_max_level = 5
        cSql = ('UPDATE core_contract SET market_max_level=%s WHERE contract_id=%d' % (market_max_level,self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id,2)
        for i in range(1,market_max_level+3):
            limitOrderPlace(self.contract_id, self.account_id, -1, i, 1)
        ret = marketOrderPlace(self.contract_id, self.account_id, 1, market_max_level)
        self.assertEqual(ret['code'], 0,'market_max_level设置为%s,限价吃单档位数与限价最大深度相同' % (market_max_level) )

        for i in range(1,market_max_level+3):
            limitOrderPlace(self.contract_id, self.account_id, -1, i, 1)
        ret = marketOrderPlace(self.contract_id, self.account_id, 1,  market_max_level+1)
        self.assertEqual(ret['code'], 1020,'limit_max_level设置为%s,限价吃单档位数大于限价最大深度相同' % (market_max_level) )

        # 设置限价最大深度为15
        orderAllCancel(self.account_id, 0)
        market_max_level = 15
        cSql = ('UPDATE core_contract SET market_max_level=%s WHERE contract_id=%d' % (market_max_level,self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id,2)
        for i in range(1,market_max_level+3):
            limitOrderPlace(self.contract_id, self.account_id, -1, i, 1)
        ret = marketOrderPlace(self.contract_id, self.account_id, 1, market_max_level)
        self.assertEqual(ret['code'], 0,'market_max_level设置为%s,限价吃单档位数与限价最大深度相同' % (market_max_level) )

        for i in range(1,market_max_level+3):
            limitOrderPlace(self.contract_id, self.account_id, -1, i, 1)
        ret = marketOrderPlace(self.contract_id, self.account_id, 1,market_max_level+1)
        self.assertEqual(ret['code'], 1020,'market_max_level设置为%s,限价吃单档位数大于限价最大深度相同' % (market_max_level) )
        orderAllCancel(self.account_id, 0)

    ## price_limit_rate 涨跌幅测试
    def test_price_limit_rate(self):
        # 设置涨跌幅为0.8
        price_limit_rate = 0.8
        cSql = ('UPDATE core_contract SET price_limit_rate=%s WHERE contract_id=%d' % (
        price_limit_rate, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id, 2)
        # 验证限价买单的涨幅
        limitOrderPlace(self.contract_id, self.account_id, -1, 5, 1)
        limitOrderPlace(self.contract_id, self.account_id, -1, 9, 1)
        limitOrderPlace(self.contract_id, self.account_id, -1, 9.1, 1)
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 9.1, 3)
        self.assertEqual(ret['code'], 1036, 'price_limit_rate验证超过范围-order price over limit')
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 9, 2)
        self.assertEqual(ret['code'], 0, 'price_limit_rate验证在范围内')
        # 验证市价买单的涨幅
        # limitOrderPlace(self.contract_id, self.account_id, -1, 5, 1)
        # limitOrderPlace(self.contract_id, self.account_id, -1, 9, 1)
        # print('查询订单')
        # time.sleep(50)
        # ret = marketOrderPlace(self.contract_id, self.account_id, 1, 3)
        # self.assertEqual(ret['code'], 1036, 'price_limit_rate验证超过范围-order price over limit')
        # ret = marketOrderPlace(self.contract_id, self.account_id, 1,  2)
        # self.assertEqual(ret['code'], 0, 'price_limit_rate验证在范围内')

        # 全部撤单
        orderAllCancel(self.account_id, 0)

        # 设置涨跌幅为2.5
        price_limit_rate = 0.6
        cSql = ('UPDATE core_contract SET price_limit_rate=%s WHERE contract_id=%d' % (
        price_limit_rate, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id, 2)
        limitOrderPlace(self.contract_id, self.account_id, 1, 5, 1)
        limitOrderPlace(self.contract_id, self.account_id, 1, 2, 1)
        limitOrderPlace(self.contract_id, self.account_id, 1, 1.9, 1)
        # 验证限价卖单的跌幅
        ret = limitOrderPlace(self.contract_id, self.account_id, -1,1.9 , 3)
        self.assertEqual(ret['code'], 1036, 'price_limit_rate验证超过范围-rder price over limit')
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, 2, 2)
        self.assertEqual(ret['code'], 0, 'price_limit_rate验证在范围内')
        # 验证市价卖单的跌幅
        # limitOrderPlace(self.contract_id, self.account_id, 1, 5, 1)
        # limitOrderPlace(self.contract_id, self.account_id, 1, 2, 1)
        # ret = marketOrderPlace(self.contract_id, self.account_id, -1, 3)
        # self.assertEqual(ret['code'], 1036, 'price_limit_rate验证超过范围-rder price over limit')
        # ret = marketOrderPlace(self.contract_id, self.account_id, -1,  2)
        # self.assertEqual(ret['code'], 0, 'price_limit_rate验证在范围内')

        # 把限制调整为100
        price_limit_rate=100
        cSql = ('UPDATE core_contract SET price_limit_rate=%s WHERE contract_id=%d' % (
        price_limit_rate, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id, 2)



    ## 合约委托数量限制 core_param_orders  优先级说明 总>指定合约>单个合约
    def test_order_nums_limit(self):

        #初始化core_param_order
        cSql = 'delete from core_param_orders'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        ret = limitOrderPlace(1,666666,1,1,1)
        self.assertEqual(ret['code'], 0, '订单数量初始化未设置参数时限制为1单-第1单正常下单')
        ret = limitOrderPlace(1, 666666, 1, 1, 1)
        self.assertEqual(ret['code'], 1028, '订单数量初始化未设置参数时限制为1单-第2单order counts is over limit')

        # 交易对id=1设置为15，单个合约为10，总下单数为30
        orderAllCancel(self.account_id, 0)
        max_num_orders_1=15
        max_num_orders_one = 10
        max_num_orders_all = 30
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, -1, %i, 15);' % (
            max_num_orders_all)
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, 0, %i, 15);' % (
            max_num_orders_one)
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, %s, %i, %i, 15);' % (
            self.account_id,self.contract_id,max_num_orders_1)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        # 特殊设置合约下单数量验证
        for i in range(0, max_num_orders_1):
            ret = limitOrderPlace(1, 666666, 1, 1, 1)
        ret = limitOrderPlace(1, 666666, 1, 1, 1)
        self.assertEqual(ret['code'], 0, '指定合约委托数量限制-范围内')
        ret = limitOrderPlace(1, 666666, 1, 1, 1)
        self.assertEqual(ret['code'], 1028, '指定合约委托数量限制-范围外order counts is over limit')
        # 非特殊设置合约
        for i in range(0,max_num_orders_one):
            ret = limitOrderPlace(2,666666,1,1,1)
        ret = limitOrderPlace(2, 666666, 1, 1, 1)
        self.assertEqual(ret['code'], 0, '单个合约委托数量限制-范围内')
        ret = limitOrderPlace(2, 666666, 1, 1, 1)
        self.assertEqual(ret['code'], 1028, '单个合约委托数量限制-范围外order counts is over limit')
        # 总合约下单数量验证
        for i in range(0,max_num_orders_all-max_num_orders_1-max_num_orders_one-1):
            ret = limitOrderPlace(3,666666,1,1,1)
        self.assertEqual(ret['code'], 0, '总合约委托数量限制-范围内')
        ret = limitOrderPlace(3, 666666, 1, 1, 1)
        self.assertEqual(ret['code'], 1028, '总合约委托数量限制-范围外order counts is over limit')

        #恢复core_param_order
        cSql = 'delete from core_param_orders'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, -1, 100, 15);'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, 0, 100, 15);'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()

    ## 特殊用户设置 core_param  core_group core_group_param
    #  优先级说明 core_param > core_group_param > core_contract
    def test_special_param(self):

        #设置core_contract 的taker_fee_ratio和 maker_fee_ratio
        taker_fee_ratio = 0.002
        maker_fee_ratio = 0.004
        cSql = ('UPDATE core_contract SET taker_fee_ratio=%s, maker_fee_ratio=%s WHERE contract_id=%d' % (
        taker_fee_ratio, maker_fee_ratio, self.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        contractPutup(self.contract_id,2)

        #初始化core_param_order
        cSql = 'delete from core_param;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group_param;'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()

        #设置core_group_param参数 并验证 contract_id=0
        contract_id=0
        group_id=1
        cSql = 'INSERT INTO `exchange`.`core_group`(`appl_id`, `variety_id`, `contract_id`, `group_id`, `user_id`) VALUES (1, 0, %s, %s, %s);' %(contract_id,group_id,self.account_id)
        operSql(cSql, 'MysqlSpot', 1)
        taker_fee_ratio_group=0.024
        maker_fee_ratio_group=0.012
        cSql = 'INSERT INTO `exchange`.`core_group_param`(`appl_id`, `contract_id`, `group_id`, `forbid_trade`, `taker_fee_ratio`, `maker_fee_ratio`, `max_num_orders`) VALUES (1, %s, %s, 0, %s, %s, 0);' %(contract_id,group_id,taker_fee_ratio_group,maker_fee_ratio_group)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()

        # 非特殊用户下单
        user_id = 666667
        orderAllCancel(self.account_id, 0)
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, user_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, user_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio),'特殊用户taker_fee_ratio校验')

        #特殊用户下单验证
        orderAllCancel(self.account_id, 0)
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_group),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_group),'特殊用户taker_fee_ratio校验')
        contract_id=2
        orderAllCancel(contract_id, 0)
        price = 1
        quality = 10
        ret = limitOrderPlace(contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_group),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_group),'特殊用户taker_fee_ratio校验')

        #设置core_group_param参数 并验证 contract_id为指定交易对
        contract_id=1
        group_id=2
        cSql = 'INSERT INTO `exchange`.`core_group`(`appl_id`, `variety_id`, `contract_id`, `group_id`, `user_id`) VALUES (1, 0, %s, %s, %s);' %(contract_id,group_id,self.account_id)
        operSql(cSql, 'MysqlSpot', 1)
        taker_fee_ratio_1=0.036
        maker_fee_ratio_1=0.015
        cSql = 'INSERT INTO `exchange`.`core_group_param`(`appl_id`, `contract_id`, `group_id`, `forbid_trade`, `taker_fee_ratio`, `maker_fee_ratio`, `max_num_orders`) VALUES (1, %s, %s, 1, %s, %s, 0);' %(contract_id,group_id,taker_fee_ratio_1,maker_fee_ratio_1)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()

        # 特殊用户在特殊交易对下单
        orderAllCancel(self.account_id, 0)
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_1),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_1),'特殊用户taker_fee_ratio校验')

        #特殊用户在普通交易对下单 校验
        contract_id = 2
        orderAllCancel(contract_id, 0)
        price = 1
        quality = 10
        ret = limitOrderPlace(contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_group),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_group),'特殊用户taker_fee_ratio校验')

        #设置core_param参数 并验证
        contract_id=0
        taker_fee_ratio_ungroup=0.014
        maker_fee_ratio_ungroup=0.028
        cSql = 'INSERT INTO `exchange`.`core_param`(`appl_id`, `contract_id`, `user_id`, `forbid_trade`, `taker_fee_ratio`, `maker_fee_ratio`) VALUES (1, %s, %s, 0, %s, %s);' %(contract_id,self.account_id,taker_fee_ratio_ungroup,maker_fee_ratio_ungroup)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()

        #core_param中特殊用户下单校验
        orderAllCancel(self.account_id, 0)
        time.sleep(1)
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_ungroup),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_ungroup),'特殊用户taker_fee_ratio校验')

        #core_param中普通用户下单校验
        # 非特殊用户下单
        user_id = 666667
        orderAllCancel(self.account_id, 0)
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, user_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, user_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio),'特殊用户taker_fee_ratio校验')


        # core_param特殊用户特殊交易对设置
        contract_id = 1
        taker_fee_ratio_ungroup_1=0.017
        maker_fee_ratio_ungroup_1=0.034
        cSql = 'INSERT INTO `exchange`.`core_param`(`appl_id`, `contract_id`, `user_id`, `forbid_trade`, `taker_fee_ratio`, `maker_fee_ratio`) VALUES (1, %s, %s, 0, %s, %s);' %(contract_id,self.account_id,taker_fee_ratio_ungroup_1,maker_fee_ratio_ungroup_1)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        # core_param中特殊用户特殊交易对下单校验
        orderAllCancel(self.account_id, 0)
        time.sleep(1)
        price = 1
        quality = 10
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(self.contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_ungroup_1),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_ungroup_1),'特殊用户taker_fee_ratio校验')
        # core_param中特殊用户非特殊交易对下单校验
        orderAllCancel(self.account_id, 0)
        time.sleep(1)
        price = 1
        quality = 10
        contract_id=2
        ret = limitOrderPlace(contract_id, self.account_id, 1, price, quality)
        bid_order_id = ret['msg']
        ret = limitOrderPlace(contract_id, self.account_id, -1, price, quality)
        ask_order_id = ret['msg']
        time.sleep(2)
        # 查询订单
        cSql = 'select * from core_match where bid_order_id=%s and ask_order_id=%s' % (bid_order_id, ask_order_id)
        result = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(float(result['bid_fee']), float(price * quality * maker_fee_ratio_ungroup),'特殊用户maker_fee_ratio校验')
        self.assertEqual(float(result['ask_fee']), float(price * quality * taker_fee_ratio_ungroup),'特殊用户taker_fee_ratio校验')


        #禁止下单验证,core_group_param core_param中的禁止下单不生效
        # contract_id=0
        # group_id=1
        # cSql = 'UPDATE  core_group_param SET forbid_trade=1 WHERE group_id=%s ' %(group_id)
        # operSql(cSql, 'MysqlSpot', 1)
        # paramRefresh5009()
        # ret = limitOrderPlace(1, self.account_id, 1, 1, 1)
        # self.assertEqual(ret['code'], 1009, '特殊用户禁止下单校验-account forbid trade')
        # ret = limitOrderPlace(2, self.account_id, 1, 1, 1)
        # self.assertEqual(ret['code'], 1009, '特殊用户禁止下单校验-account forbid trade')
        #
        # cSql = 'UPDATE  core_group_param SET forbid_trade=0 WHERE group_id=%s ' %(group_id)
        # operSql(cSql, 'MysqlSpot', 1)
        # contract_id=1
        # group_id=2
        # cSql = 'UPDATE  core_group_param SET forbid_trade=1 WHERE group_id=%s ' %(group_id)
        # operSql(cSql, 'MysqlSpot', 1)
        # paramRefresh5009()
        # ret = limitOrderPlace(1, self.account_id, 1, 1, 1)
        # self.assertEqual(ret['code'], 1009, '特殊用户禁止下单校验-account forbid trade')
        # ret = limitOrderPlace(2, self.account_id, 1, 1, 1)
        # self.assertEqual(ret['code'], 0, '允许下单')
        # cSql = 'UPDATE  core_group_param SET forbid_trade=0 WHERE group_id=%s ' %(group_id)
        # operSql(cSql, 'MysqlSpot', 1)
        # paramRefresh5009()
        # ret = limitOrderPlace(2, self.account_id, 1, 1, 1)
        # self.assertEqual(ret['code'], 0, '允许下单')

        cSql = 'UPDATE  core_param SET forbid_trade=1 WHERE contract_id=%s AND user_id=%s' %(self.contract_id,self.account_id)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        ret = limitOrderPlace(self.contract_id, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1009,'特殊用户禁止下单校验-account forbid trade')
        ret = limitOrderPlace(2, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 0, '允许下单')
        cSql = 'UPDATE  core_param SET forbid_trade=1 WHERE contract_id=%s AND user_id=%s' %(0,self.account_id)
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        ret = limitOrderPlace(2, self.account_id, 1, 1, 1)
        self.assertEqual(ret['code'], 1009,'特殊用户禁止下单校验-account forbid trade')


        #恢复用户下单权限及恢复手续费
        cSql = 'UPDATE  core_param SET forbid_trade=0 WHERE contract_id=%s AND user_id=%s' % (
        self.contract_id, self.account_id)
        operSql(cSql, 'MysqlSpot', 1)
        #初始化core_param_order
        cSql = 'delete from core_param;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group_param;'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()




















