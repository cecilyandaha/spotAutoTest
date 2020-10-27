import  unittest

from zmq_util_instract import cancelAllUsersOrders
from zmq_spot_instruct import *
from util import *

class TestContractParam(unittest.TestCase):
    contract_id=1
    account_id=666666
    core_order_X = 'core_order_' + str(account_id % 10)

    @classmethod
    def setUpClass(cls):
        print ("this setUpClass() method only called once .\n")
        cSql = ('UPDATE core_contract SET price_limit_rate=100 ,market_max_level=10,limit_max_level=10 ,taker_fee_ratio=0.006,maker_fee_ratio=0.003, contract_status=2 WHERE contract_id=%d' % (cls.contract_id))
        operSql(cSql, 'MysqlSpot', 1)
        print ("this setupclass() method only called once.\n")
        cSql = 'delete from core_param;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_group_param;'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'delete from core_param_orders'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, -1, 100, 15);'
        operSql(cSql, 'MysqlSpot', 1)
        cSql = 'INSERT INTO `exchange`.`core_param_orders`(`appl_id`, `user_id`, `contract_id`, `max_num_orders`, `max_num_condition_orders`) VALUES (1, 0, 0, 100, 15);'
        operSql(cSql, 'MysqlSpot', 1)
        paramRefresh5009()
        contractPutup(cls.contract_id, 2)

    @classmethod
    def tearDownClass(cls):
        print ("this teardownclass() method only called once too.\n")

    def setUp(self):
        # 先全部撤单以免下单数量超过限制
        cancelAllUsersOrders()
        print ("do something before test : prepare environment.\n")
    def tearDown(self):
        print ("do something after test : clean up.\n")

    # # 测试core_order数据 ,包含测试了撤单接口
    def test_core_order(self):

        #正常下单委托 状态为已申报未成交2
        # 交易对、用户id、方向、价格、数量、order_type、order_status、filled_currency成交金额、filled_quantity成交数量、canceled_quantity撤销数量、frozen_price冻结价格
        list2_1=[self.contract_id,self.account_id,-1,10.0,1.1,1,2,0.0,0.0,0.0,10.0]
        ret2 = limitOrderPlace(list2_1[0],list2_1[1],list2_1[2],list2_1[3],list2_1[4])
        list2_1.append(ret2['cl_seq_id'])
        time.sleep(3)
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret2['msg'])
        print(cSql)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        list2_2=[order1['contract_id'],order1['user_id'],order1['side'],float(order1['price']),float(order1['quantity'])
            ,order1['order_type'],order1['order_status'],float(order1['filled_currency']),float(order1['filled_quantity'])
            ,float(order1['canceled_quantity']),float(order1['frozen_price']),order1['client_order_id']]
        self.assertListEqual(list2_1,list2_2,'限价下单-状态为已申报未成交2')

        #正常下单委托 部分成交-3
        #  交易对0、用户id1、方向2、价格3、数量4、order_type5、状态6、filled_currency成交金额7、filled_quantity成交数量8、canceled_quantity撤销数量9、frozen_price冻结价格10、client_order_id11
        list3_1=[self.contract_id,self.account_id,1,12.0,4.0,1,3,0,0,0.0,12.0]
        ret3 = limitOrderPlace(list3_1[0],list3_1[1],list3_1[2],list3_1[3],list3_1[4])
        list3_1.append(ret3['cl_seq_id'])
        list3_1[7]=list2_1[3] * list2_1[4]
        list3_1[8] = list2_1[4]
        time.sleep(3)
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret3['msg'])
        print(cSql)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        list3_2=[order1['contract_id'],order1['user_id'],order1['side'],float(order1['price']),float(order1['quantity'])
            ,order1['order_type'],order1['order_status'],dataTransform(order1['filled_currency']),dataTransform(order1['filled_quantity'])
            ,dataTransform(order1['canceled_quantity']),dataTransform(order1['frozen_price']),order1['client_order_id']]
        self.assertListEqual(list3_1,list3_2,'限价下单-状态为部分成交3')


        # 正常下单委托 完全成交-4 部分撤单-5
        #  交易对0、用户id1、方向2、价格3、数量4、order_type5、状态6、filled_currency成交金额7、filled_quantity成交数量8、canceled_quantity撤销数量9、frozen_price冻结价格10、client_order_id11
        list3_1[6]=4
        list3_1[7] = list3_1[7]+list3_1[3]*(list3_1[4]-list2_1[4])
        list3_1[8] = list3_1[4]
        list4_1=[self.contract_id,self.account_id,-1,12.0,5+list3_1[4]-list2_1[4],1,3,0,0,0.0,12.0]
        ret4 = limitOrderPlace(list4_1[0],list4_1[1],list4_1[2],list4_1[3],list4_1[4])
        list4_1.append(ret4['cl_seq_id'])
        list4_1[7]=list3_1[3]*(list3_1[4]-list2_1[4])
        list4_1[8] = list3_1[4]-list2_1[4]
        time.sleep(3)
        # 验证完全成交-4
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret3['msg'])
        print(cSql)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        list3_2=[order1['contract_id'],order1['user_id'],order1['side'],float(order1['price']),float(order1['quantity'])
            ,order1['order_type'],order1['order_status'],dataTransform(order1['filled_currency']),dataTransform(order1['filled_quantity'])
            ,dataTransform(order1['canceled_quantity']),dataTransform(order1['frozen_price']),order1['client_order_id']]
        self.assertListEqual(list3_1, list3_2, '限价下单-状态为部分成交4')

        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret4['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        # 验证部分撤单-5 验证撤单
        list4_2=[order1['contract_id'],order1['user_id'],order1['side'],float(order1['price']),float(order1['quantity'])
            ,order1['order_type'],order1['order_status'],dataTransform(order1['filled_currency']),dataTransform(order1['filled_quantity'])
            ,dataTransform(order1['canceled_quantity']),dataTransform(order1['frozen_price']),order1['client_order_id']]
        self.assertListEqual(list4_1,list4_2,'限价下单-状态为部分成交3')
        #撤单
        cancel = orderCancel(self.account_id,self.contract_id,ret4['msg'])
        time.sleep(3)
        list4_1[6]=5
        list4_1[9] = list4_1[4]-list4_1[8]
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret4['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        list4_2=[order1['contract_id'],order1['user_id'],order1['side'],float(order1['price']),float(order1['quantity'])
            ,order1['order_type'],order1['order_status'],dataTransform(order1['filled_currency']),dataTransform(order1['filled_quantity'])
            ,dataTransform(order1['canceled_quantity']),dataTransform(order1['frozen_price']),order1['client_order_id']]
        self.assertListEqual(list4_1,list4_2,'限价下单-状态为部分成交5')
        print(list4_1)

        # 正常下单委托 完全撤单-6
        #  交易对0、用户id1、方向2、价格3、数量4、order_type5、状态6、filled_currency成交金额7、filled_quantity成交数量8、canceled_quantity撤销数量9、frozen_price冻结价格10、client_order_id11
        list6_1=[self.contract_id,self.account_id,1,1.0,1.0,1,6,0.0,0.0,1.0,1.0]
        ret6 = limitOrderPlace(list6_1[0],list6_1[1],list6_1[2],list6_1[3],list6_1[4])
        list6_1.append(ret6['cl_seq_id'])
        time.sleep(3)
        orderCancel(self.account_id, self.contract_id, ret6['msg'])
        time.sleep(3)
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret6['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        list6_2=[order1['contract_id'],order1['user_id'],order1['side'],float(order1['price']),float(order1['quantity'])
            ,order1['order_type'],order1['order_status'],dataTransform(order1['filled_currency']),dataTransform(order1['filled_quantity'])
            ,dataTransform(order1['canceled_quantity']),dataTransform(order1['frozen_price']),order1['client_order_id']]
        self.assertListEqual(list6_1,list6_2,'限价下单-状态为部分成交5')

        ## order_type市价验证
        limitOrderPlace(self.contract_id,self.account_id,1,1.0,1.0)
        ret7 = marketOrderPlace(self.contract_id,self.account_id,-1,1.0)
        time.sleep(3)
        cSql = 'select * from %s where uuid="%s"' % (self.core_order_X, ret7['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(order1['order_type'], 3, '市价下单-order_type为3')


    # # 测试 core_match表数据，包含了撤单和一键撤单 手续费字段在手续费设置处已进行测试
    def test_core_match(self):

        # bid_user_id0 ask_user_id1 bid_order_id2 ask_order_id3 match_price4 match_qty5 match_amt6 is_taker7
        account_id2=666667
        orderAllCancel(account_id2,0)
        match_price=1.5
        match_qty=1.8
        ret1 = limitOrderPlace(self.contract_id,self.account_id,1,match_price,match_qty)
        ret2 = limitOrderPlace(self.contract_id, account_id2, -1,match_price,match_qty)
        time.sleep(3)
        cSql = 'select * from core_match where bid_order_id="%s" and ask_order_id="%s"' % (ret1['msg'],ret2['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual([self.account_id,      account_id2,          ret1['msg'],           ret2['msg'],           match_price,          match_qty,          match_price*match_qty,-1],
                         [order1['bid_user_id'],order1['ask_user_id'],order1['bid_order_id'],order1['ask_order_id'],dataTransform(order1['match_price']),dataTransform(order1['match_qty']),dataTransform(order1['match_amt']),order1['is_taker']], 'core_match测试1')

        ret1 = limitOrderPlace(self.contract_id,self.account_id,-1,match_price,match_qty)
        ret2 = limitOrderPlace(self.contract_id, account_id2, 1,match_price,match_qty)
        time.sleep(3)
        cSql = 'select * from core_match where bid_order_id="%s" and ask_order_id="%s"' % (ret2['msg'],ret1['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual([account_id2,     self.account_id ,          ret2['msg'],           ret1['msg'],           match_price,          match_qty,          match_price*match_qty,1],
                         [order1['bid_user_id'],order1['ask_user_id'],order1['bid_order_id'],order1['ask_order_id'],dataTransform(order1['match_price']),dataTransform(order1['match_qty']),dataTransform(order1['match_amt']),order1['is_taker']], 'core_match测试1')

    # # 批量下单撤单测试
    def test_batch_order_and_cancel(self):

        #批量下单
        time.sleep(3)
        # contract_id,order_type,side,order_price,order_qty,client_order_id
        orders = [[self.contract_id, 1, 1, 1.1, 2.1, 1001],
         [self.contract_id, 1, 1, 1.2, 2.2, 1002],
         [self.contract_id, 1, 1, 1.3, 2.3, 1003],
         [self.contract_id, 1, 1, 1.4, 2.4, 1004],
         [self.contract_id, 1, 1, 1.5, 2.5, 1005],
         [self.contract_id, 1, 1, 1.6, 2.6, 1006],
         [self.contract_id, 1, 1, 1.7, 2.7, 1007],
         [self.contract_id, 1, 1, 1.8, 2.8, 1008],
         [self.contract_id, 1, 1, 1.9, 2.9, 1009],
         [self.contract_id, 1, 1, 2.0, 3.0, 1010],
         [self.contract_id, 1, -1, 4.1, 5.1, 2001],
         [self.contract_id, 1, -1, 4.2, 5.2, 2002],
         [self.contract_id, 1, -1, 4.3, 5.3, 2003],
         [self.contract_id, 1, -1, 4.4, 5.4, 2004],
         [self.contract_id, 1, -1, 4.5, 5.5, 2005],
         [self.contract_id, 1, -1, 4.6, 5.6, 2006],
         [self.contract_id, 1, -1, 4.7, 5.7, 2007],
         [self.contract_id, 1, -1, 4.8, 5.8, 2008],
         [self.contract_id, 1, -1, 4.9, 5.9, 2009],
         [self.contract_id, 1, -1, 5.0, 6.0, 2010]
         ]
        ret = orderPlaceBatch(self.account_id,orders)
        succ = json.loads(ret['msg'])
        time.sleep(5)
        succList=[]
        for i,msg in enumerate(succ['succ']):
            cSql = 'select * from %s where uuid="%s"' % (self.core_order_X, msg[1])
            order1 = operSql(cSql, 'MysqlSpot', 1)
            list2 = [order1['contract_id'], order1['order_type'], order1['side'], dataTransform(order1['price']),dataTransform(order1['quantity'])]
            self.assertListEqual(list2,orders[i][0:5],'批量下单测试')
            succList.append([self.contract_id, msg[1],i])

        #批量撤单
        # contract_id0  original_order_id1 client_order_id2
        orderBatchCancel(self.account_id,succList)
        time.sleep(5)
        for msg in succ['succ']:
            cSql = 'select * from %s where uuid="%s"' % (self.core_order_X, msg[1])
            order1 = operSql(cSql, 'MysqlSpot', 1)
            self.assertEqual(order1['order_status'], 6, '批量撤单测试')

    # #划转测试 core_account测试
    def test_transfer(self):

        # 新账户划转到现货
        cSql = 'select * from core_account order by user_id DESC limit 0,1'
        order1 = operSql(cSql, 'MysqlSpot', 1)
        user_id = order1['user_id']+1
        currency_id =2
        quantity1 = 123456.123456789
        spotAddMoney(user_id,currency_id,quantity1 )
        time.sleep(3)
        cSql = 'select * from core_account where user_id=%s and  currency_id=%s ' %(user_id,currency_id)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(dataTransform(order1['total_money'],digit = 10), quantity1, '划转到现货')

        # 现货划出
        quantity2 = 113456.123456779
        spotminusMoney(user_id,currency_id,quantity2 )
        time.sleep(3)
        cSql = 'select * from core_account where user_id=%s and  currency_id=%s ' %(user_id,currency_id)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(dataTransform(order1['total_money'],digit = 10), dataTransform(quantity1-quantity2,digit = 10), '划转出现货')

        #老账户划转极限值验证
        quantity3 = 123456789012345678.123456789
        spotAddMoney(user_id,currency_id,quantity3 )
        time.sleep(3)
        cSql = 'select * from core_account where user_id=%s and  currency_id=%s ' %(user_id,currency_id)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(dataTransform(order1['total_money'],digit = 9), dataTransform(quantity1-quantity2+quantity3,digit = 10), '划转到现货-极限值')

        #划转到其他币种
        quantity4 = 1000
        currency_id2=3
        spotAddMoney(user_id, currency_id2, quantity4)
        time.sleep(3)
        cSql = 'select * from core_account where user_id=%s and  currency_id=%s ' % (user_id, currency_id2)
        print(cSql)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        self.assertEqual(dataTransform(order1['total_money']),
                         dataTransform(quantity4), '划转到现货-其他交易对')

        #账户是否能划转后小于0
        quantity5 = 1001
        currency_id2=3
        spotminusMoney(user_id, currency_id2, quantity5)
        time.sleep(3)
        cSql = 'select * from core_account where user_id=%s and  currency_id=%s ' % (user_id, currency_id2)
        print(cSql)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        self.assertEqual(dataTransform(order1['total_money']),
                         dataTransform(quantity4), '划转到现货-其他交易对')


        # 新账户创建直接划出 报账号不存在
        cSql = 'select * from core_account order by user_id DESC limit 0,1'
        order1 = operSql(cSql, 'MysqlSpot', 1)
        user_id = order1['user_id']+1
        currency_id =2
        quantity1 = 1
        spotminusMoney(user_id, currency_id, quantity2)
        time.sleep(3)
        cSql = 'select * from core_account where user_id=%s and  currency_id=%s ' % (user_id, currency_id)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertIsNone(order1,'新账号划转出现货')

    # 下单资金验证及冻结资金验证
    def test_order_capital_verification(self):
        cSql = 'select * from core_contract where contract_id=%s  ' % (self.contract_id)
        order1 = operSql(cSql, 'MysqlSpot', 1)
        taker_fee_ratio = dataTransform(order1['taker_fee_ratio'])
        maker_fee_ratio = dataTransform(order1['maker_fee_ratio'])

        #限价下单资金验证
        match_price=1000
        match_qty=1
        cSql = 'select * from core_account order by user_id DESC limit 0,1'
        order1 = operSql(cSql, 'MysqlSpot', 1)
        user_id = order1['user_id']+1
        currency_id = 2
        quantityM = 0.1
        quantity1 = match_price*match_qty*(1+taker_fee_ratio)-quantityM
        spotAddMoney(user_id,currency_id,quantity1 )
        time.sleep(3)
        ret1 = limitOrderPlace(self.contract_id,user_id,1,match_price,match_qty)
        self.assertEqual(ret1['code'], 1007,'限价下单资金不足校验-下单验证的时候是用taker费率来判断余额是否充足avail not enough')
        spotAddMoney(user_id,currency_id,quantityM )
        time.sleep(3)
        ret1 = limitOrderPlace(self.contract_id, user_id, 1, match_price, match_qty)
        time.sleep(3)
        self.assertEqual(ret1['code'], 0,'限价下单资金刚可以通过校验-下单验证的时候是用taker费率来判断余额是否充足')


        # 判断冻结金额
        cSql = 'select * from core_account where  user_id=%s and currency_id=%s' %(user_id,currency_id)
        ret1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(dataTransform(ret1['order_frozen_money']), dataTransform(match_price*match_qty*(1+maker_fee_ratio)), '现货下单后验证冻结金额按照maker冻结')
        #再下一笔单 校验冻结金额
        spotAddMoney(user_id, currency_id, dataTransform(ret1['total_money']))
        time.sleep(3)
        ret1 = limitOrderPlace(self.contract_id, user_id, 1, match_price, match_qty)
        cSql = 'select * from core_account where  user_id=%s and currency_id=%s' % (user_id, currency_id)
        ret1 = operSql(cSql, 'MysqlSpot', 1)
        self.assertEqual(dataTransform(ret1['order_frozen_money']), dataTransform(2*match_price * match_qty * (1 + maker_fee_ratio)),'多笔委托冻结金额验证')

        #市价下单资金验证
        cancelAllUsersOrders()
        orders = [
         [self.contract_id, 1, 1, 1, 10, 1001],
         [self.contract_id, 1, 1, 2, 20, 1002],
         [self.contract_id, 1, 1, 3, 30, 1003],
         [self.contract_id, 1, -1, 5, 10, 2008],
         [self.contract_id, 1, -1, 6, 20, 2009],
         [self.contract_id, 1, -1, 7, 30, 2010]
         ]
        ret = orderPlaceBatch(self.account_id,orders)
        match_price=7
        match_qty=40
        cSql = 'select * from core_account order by user_id DESC limit 0,1'
        order1 = operSql(cSql, 'MysqlSpot', 1)
        user_id = order1['user_id']+1
        currency_id = 2
        quantityM = 0.1
        quantity1 = match_price*match_qty*(1+taker_fee_ratio)-quantityM
        spotAddMoney(user_id,currency_id,quantity1 )
        time.sleep(3)
        ret1 = marketOrderPlace(self.contract_id,user_id,1,match_qty)
        self.assertEqual(ret1['code'], 1007,'市价下单资金不足校验-下单验证的时候是用taker费率来判断余额是否充足avail not enough')
        spotAddMoney(user_id,currency_id,quantityM )
        time.sleep(3)
        ret1 = marketOrderPlace(self.contract_id, user_id, 1,match_qty)
        time.sleep(3)
        self.assertEqual(ret1['code'], 0,'市价下单资金刚可以通过校验-下单验证的时候是用taker费率来判断余额是否充足')

        # 市价下单判断商品货币数量是否充足
        user_id = user_id+1
        spotAddMoney(user_id, 3, 1)
        ret1 = marketOrderPlace(self.contract_id, user_id, -1,1.01)
        self.assertEqual(ret1['code'], 1008,'市价卖单数量不足-quantity not enoug')
        ret1 = marketOrderPlace(self.contract_id, user_id, -1, 1)
        self.assertEqual(ret1['code'], 0,'市价卖单数量充足')

        # 限价下单判断商品货币数量是否充足
        spotAddMoney(user_id, 3, 1)
        ret1 = limitOrderPlace(self.contract_id, user_id, -1, match_price, 1.01)
        self.assertEqual(ret1['code'], 1008,'限价卖单数量不足-quantity not enoug')
        ret1 = limitOrderPlace(self.contract_id, user_id, -1, match_price, 1)
        self.assertEqual(ret1['code'], 0,'限价卖单数量充足')

    # 市价下单 对手方不足的情况测试
    def test_market_order(self):
        # 市价下单 对手方数量为0
        ret1 = marketOrderPlace(self.contract_id, self.account_id, -1,10)
        self.assertEqual(ret1['code'], 1020,'市价卖单无无对手方-counter party order no exist')
        ret1 = marketOrderPlace(self.contract_id, self.account_id, 1,10)
        self.assertEqual(ret1['code'], 1020,'市价买单无无对手方-counter party order no exist')

        # 市价下单 对手方数量小于市价下单数量有多少吃多少
        orders = [
         [self.contract_id, 1, 1, 10, 10, 1001],
         [self.contract_id, 1, 1, 11, 20, 1002],
         [self.contract_id, 1, 1, 12, 30, 1003],
         [self.contract_id, 1, -1, 20, 10, 2008],
         [self.contract_id, 1, -1, 21, 20, 2009],
         [self.contract_id, 1, -1, 22, 30, 2010]
         ]
        ret = orderPlaceBatch(self.account_id,orders)
        # 市价下单 对手方数量小于市价数量
        quantity=100
        ret1 = marketOrderPlace(self.contract_id, self.account_id, -1,quantity)
        time.sleep(3)
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret1['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        #price,quantity,order_type,order_status,filled_currency,filled_quantity,canceled_quantity,frozen_price
        list1_1 = [0, quantity, 3, 5, 680, 60, 40, 10]
        list1_2 =[dataTransform(order1['price']),dataTransform(order1['quantity']),order1['order_type'],order1['order_status'],
                  dataTransform(order1['filled_currency']),dataTransform(order1['filled_quantity']),dataTransform(order1['canceled_quantity']),dataTransform(order1['frozen_price']) ]
        self.assertListEqual(list1_1, list1_2, '市价卖单-挂单小于市价委托数量')
        ret1 = marketOrderPlace(self.contract_id, self.account_id, 1,quantity)
        time.sleep(3)
        cSql = 'select * from %s where uuid="%s"' %(self.core_order_X,ret1['msg'])
        order1 = operSql(cSql, 'MysqlSpot', 1)
        print(order1)
        list2_1 = [0, quantity, 3, 5, 1280, 60, 40, 22]
        list2_2 = [dataTransform(order1['price']), dataTransform(order1['quantity']), order1['order_type'],order1['order_status'],
                   dataTransform(order1['filled_currency']), dataTransform(order1['filled_quantity']),
                   dataTransform(order1['canceled_quantity']), dataTransform(order1['frozen_price'])]
        self.assertListEqual(list2_1, list2_2, '市价买单-挂单小于市价委托数量')

    # 批量转账测试 0 account_id 1 currency_id  2 from_appl_id 3 to_appl_id 4 quantity
    def test_transfer_batch(self):
        cSql = 'select * from core_account order by user_id DESC limit 0,1'
        order1 = operSql(cSql, 'MysqlSpot', 1)
        user_id = order1['user_id']+1
        transfers=[
            [user_id,     1, 5, 1, 100.123456],
            [user_id,     2, 5, 1, 200.12345678],
            [user_id,     3, 5, 1, 300],
            [user_id + 1, 1, 5, 1, 10000001],
            [user_id + 1, 1, 5, 1, 2232323],
            [user_id + 1, 3, 5, 1, 10000001],
            [user_id + 2, 2, 5, 1, 123455],
            [user_id + 3, 1, 5, 1, 123455],
            [user_id,     1, 1, 5, 50],
            [user_id,     2, 5, 1, 121212],
            [user_id,     2, 1, 5, 2.2356],
        ]
        transferBatch(transfers)
        tranMap={}
        for transfer in transfers:
            if transfer[0] in tranMap :
                if transfer[1] in tranMap[transfer[0]] :
                    if transfer[3] == 1:
                        tranMap[transfer[0]][transfer[1]] += transfer[4]
                    elif tranMap[transfer[0]][transfer[1]] > transfer[4]:
                        tranMap[transfer[0]][transfer[1]] -= transfer[4]
                else:
                    if transfer[3] == 1:
                        tranMap[transfer[0]][transfer[1]] =transfer[4]
                    else:
                        tranMap[transfer[0]][transfer[1]] =0
            else:
                if transfer[3]==1:
                    tranMap[transfer[0]]={transfer[1]:transfer[4]}
                else:
                    tranMap[transfer[0]]={transfer[1]:0}
        for key in tranMap:
            for k in tranMap[key]:
                cSql = 'select * from core_account where user_id=%s and currency_id=%s ' %(key,k)
                order1 = operSql(cSql, 'MysqlSpot', 1)
                self.assertEqual(dataTransform(tranMap[key][k]),dataTransform(order1['total_money']) , '批量划转')





































