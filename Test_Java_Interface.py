import random
import time
import unittest

from zmq_util_instract import cancelAllUsersOrders, operSql, decimal_trans, dataTransform, contractDelist
from java_Interface import *

class TestJavaInterface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 将所有的合约都下架 然后清空数据库中的core_contract和core_quot
        cSql='select * from core_contract'
        results = operSql(cSql, 'MysqlSpot')
        for result in results:
            contractDelist(result['contract_id'])
        cSql='delete from core_contract'
        results = operSql(cSql, 'MysqlSpot',1)
        cSql = 'delete from core_quot'
        results = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(2)
        print("已经所有合约下线并从数据库中清除")



    @classmethod
    def tearDownClass(cls):
        print ("this teardownclass() method only called once too.\n")

    def setUp(self):
        print ("do something before test : prepare environment.\n")

    def tearDown(self):
        print ("do something after test : clean up.\n")


    ## 新增交易对接口测试
    def test_pairs_insert(self):
        # 用例1正常新增交易对，合约状态在新增时默认为5
        # 用例2新增交易对多余字段不会被写入
        paradic = {
            "commodityId": 2,
            "currencyId": 1,
            "kycMatchLevel": 0,
            "limitMaxLevel": 10,
            "listPrice": 6,
            "listTime": 1603160722000,
            "lotSize": "0.010000000000000000",
            "makerFeeRatio": "0.000300000000000000",
            "marketMaxLevel": 11,
            "maxNumOrders": 12,
            "priceLimitRate": 0.01,
            "priceTick": "0.000100000000000000",
            "sort": 2,
            "symbol": "USDT-CNYT",
            "takerFeeRatio": "0.000600000000000000",
            "type": "SPOT",
            "contractStatus":2 # 该字段为多余字段
        }
        pairs_insert(paradic)
        time.sleep(5)
        paradic['contractStatus']=5
        interData = pairs_get()['text']['data'][0]
        self.assertEqual(len(paradic.keys() & interData.keys()), len(paradic.items() & interData.items()), '14项数据相同')

        # 用例3已经新增的合约再次新增 报错 pair already exist
        result = pairs_insert(paradic1)
        self.assertEqual(result['status'],500,'重复新增同一个合约')

        # 用例4新增合约的部分字段范围测试


    ## 获取所有合约接口测试
    def test_pairs_get(self):
        interData = pairs_get()['text']['data']
        cSql='select * from core_contract'
        sqlDatas = operSql(cSql, 'MysqlSpot')
        for i in range(len(interData)):
            Inter=interData[i]
            Sql = decimal_trans(sqlDatas[i])
            self.assertEqual(Sql['contract_id'],Inter['contractId'] , 'contract_id')
            self.assertEqual('SPOT', Inter['type'], '合约id')
            self.assertEqual(Sql['symbol'], Inter['symbol'], 'symbol')
            self.assertEqual(Sql['commodity_id'], Inter['commodityId'], 'commodity_id')
            self.assertEqual(Sql['currency_id'], Inter['currencyId'], 'currency_id')
            self.assertEqual(Sql['price_tick'], Inter['rawPriceTick'], 'price_tick')
            self.assertEqual(Sql['lot_size'], Inter['rawLotSize'], 'lot_size')
            self.assertEqual(Sql['taker_fee_ratio'], dataTransform(Inter['takerFeeRatio']), 'taker_fee_ratio')
            self.assertEqual(Sql['maker_fee_ratio'], dataTransform(Inter['makerFeeRatio']), 'maker_fee_ratio')
            self.assertEqual(Sql['market_max_level'], (Inter['marketMaxLevel']), 'taker_fee_ratio')
            self.assertEqual(Sql['limit_max_level'], (Inter['limitMaxLevel']), 'limit_max_level')
            self.assertEqual(Sql['price_limit_rate'], (Inter['priceLimitRate']), 'price_limit_rate')
            self.assertEqual(Sql['max_num_orders'], (Inter['maxNumOrders']), 'max_num_orders')
            self.assertEqual(Sql['contract_status'], (Inter['contractStatus']), 'contractStatus')
            self.assertEqual(Sql['kyc_match_level'], (Inter['kycMatchLevel']), 'kyc_match_level')
            self.assertEqual(Sql['list_price'], (Inter['listPrice']), 'list_price')


    ## 更新交易对接口测试
    def test_pairs_update(self):
        # 用例1 对所有允许修改的字段都做修改
        #      更新未上线合约参数
        # 用例5 更新不允许修改的参数 不允许修改的字段不被修改

        interData1 = pairs_get()['text']['data'][0]
        cSql = 'update core_contract set contract_status=5 where contract_id=%s' % (interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        interData1['contract_status']=5
        time.sleep(5)
        print(interData1)
        paradic1 = {
            "contractId": interData1['contractId'],
            "applId": 1,
            "kycMatchLevel": 3,
            "limitMaxLevel": 3,
            "listPrice": 15,
            "listTime": 1603160722000,
            "lotSize": "0.000010000000000000",
            "makerFeeRatio": "0.010000000000000000",
            "marketMaxLevel": 4,
            "maxNumOrders": 20,
            "priceLimitRate": 1.1,
            "priceTick": "0.001000000000000000",
            "sort": 3,
            "takerFeeRatio": "0.000300000000000000",
            "type": "SPOT",
            "updateType": 3,
            "contractStatus": 1, #该字段为不允许修改的字段
            "commodityId":interData1['commodityId'], #该字段为不允许修改的字段
            "currencyId":interData1['currencyId'] #该字段为不允许修改的字段
        }
        pairs_update(paradic1)
        time.sleep(5)
        interData2 = pairs_get()['text']['data'][0]
        paradic1['contractStatus']=5
        self.assertEqual(len(paradic1.keys() & interData2.keys()), len(paradic1.items() & interData2.items()), '16项数据相同')

        # 用例2 更新已下线合约参数
        cSql='update core_contract set contract_status=4 where contract_id=%s' %(interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot',1)
        paradic1['takerFeeRatio'] = '0.000600000000000000'
        paradic1['contractStatus'] = 4
        pairs_update(paradic1)
        time.sleep(5)
        interData3 = pairs_get()['text']['data'][0]
        self.assertEqual(len(paradic1.keys() & interData3.keys()), len(paradic1.items() & interData3.items()), '16项数据相同')

        # 用例3 更新已上线合约参数 不允许修改
        cSql='update core_contract set contract_status=2 where contract_id=%s' %(interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot',1)
        time.sleep(5)
        result = pairs_update(paradic1)
        self.assertEqual(result['status'], 500, '在线合约不允许修改')

        # 用例4 更新暂停状态合约参数 不允许修改
        cSql='update core_contract set contract_status=3 where contract_id=%s' %(interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot',1)
        time.sleep(5)
        result = pairs_update(paradic1)
        self.assertEqual(result['status'], 500, '在线合约不允许修改')

        # 用例5 部分字段极限值测试 不测试


    ## kyc可交易等级，展示权重变更参数接口测试
    def test_pairs_otherParam(self):
        # 用例1 未上线状态修改2个参数
        # 用例4 修改其它参数不生效
        interData1 = pairs_get()['text']['data'][0]
        cSql = 'update core_contract set contract_status=5 where contract_id=%s' % (interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(3)
        paradic = {
            "contractId": interData1['contractId'],
            "applId": 1,
            "kycMatchLevel": random.randrange(0,3),
            "sort": random.randrange(0,10000),
            "type": "SPOT",
            "updateType": 2,
            "contractStatus":1  #该字段为不允许修改的字段
        }
        result=  pairs_update(paradic)
        time.sleep(3)
        interData1 = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['kycMatchLevel'],interData1['kycMatchLevel'],'核对kycMatchLevel')
        self.assertEqual(paradic['sort'], interData1['sort'], '核对sort')
        self.assertNotEqual(paradic['contractStatus'], 5, '核对contractStatus')

        # 用例2 上线状态修改2个参数
        cSql = 'update core_contract set contract_status=2 where contract_id=%s' % (interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(3)
        paradic = {
            "contractId": interData1['contractId'],
            "applId": 1,
            "kycMatchLevel": random.randrange(0,3),
            "sort": random.randrange(0,10000),
            "type": "SPOT",
            "updateType": 2,
        }
        result=  pairs_update(paradic)
        time.sleep(3)
        interData1 = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['kycMatchLevel'],interData1['kycMatchLevel'],'核对kycMatchLevel')
        self.assertEqual(paradic['sort'], interData1['sort'], '核对sort')

        # 用例3 下线状态修改2个参数
        cSql = 'update core_contract set contract_status=3 where contract_id=%s' % (interData1['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(3)
        paradic = {
            "contractId": interData1['contractId'],
            "applId": 1,
            "kycMatchLevel": random.randrange(0,3),
            "sort": random.randrange(0,10000),
            "type": "SPOT",
            "updateType": 2,
        }
        result=  pairs_update(paradic)
        time.sleep(3)
        interData1 = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['kycMatchLevel'],interData1['kycMatchLevel'],'核对kycMatchLevel')
        self.assertEqual(paradic['sort'], interData1['sort'], '核对sort')


    ## 上下线交易对接口测试
    def test_pairs_updwon(self):
        # 用例1 状态为未上市的合约上线
        interData = pairs_get()['text']['data'][0]
        cSql = 'update core_contract set contract_status=5 where contract_id=%s' % (interData['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(3)
        paradic = {
            "contractId": interData['contractId'],
            "applId": 1,
            "contractStatus": 2,
            "type": "SPOT",
            "updateType": 1
        }
        pairs_update(paradic)
        time.sleep(3)
        interData = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['contractStatus'], interData['contractStatus'], '状态为未上市的合约上线')

        # 用例2 状态为上线中的合约上线 不允许重复上线
        result = pairs_update(paradic)
        self.assertEqual(result['status'], 500, '状态为上线中的合约上线不允许再上线')

        # 用例3 状态为暂停中的合约上线 不允许重复上线
        cSql = 'update core_contract set contract_status=3 where contract_id=%s' % (interData['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(3)
        paradic['contractStatus'] = 3
        result = pairs_update(paradic)
        self.assertEqual(result['status'], 500, '状态为上线中的合约上线不允许再上线')

        # 用例4 状态为已上线的合约下线
        cSql = 'update core_contract set contract_status=2 where contract_id=%s' % (interData['contractId'])
        sqlDatas = operSql(cSql, 'MysqlSpot', 1)
        time.sleep(3)
        paradic['contractStatus'] =4
        pairs_update(paradic)
        time.sleep(3)
        interData = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['contractStatus'], interData['contractStatus'], '状态为已上线的合约下线')

        # 用例5 状态为下线的合约上线
        paradic['contractStatus'] = 2
        result = pairs_update(paradic)
        time.sleep(3)
        interData = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['contractStatus'], interData['contractStatus'], '状态为下线的合约上线')

        # 用例6 状态为上线的合约改为暂停
        paradic['contractStatus'] = 3
        result = pairs_update(paradic)
        time.sleep(3)
        interData = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['contractStatus'], interData['contractStatus'], '状态为上线的合约改为暂停')

        # 用例6 状态为暂停中的合约下线
        paradic['contractStatus'] =4
        pairs_update(paradic)
        time.sleep(3)
        interData = pairs_get()['text']['data'][0]
        self.assertEqual(paradic['contractStatus'], interData['contractStatus'], '状态为暂停中的合约下线')





