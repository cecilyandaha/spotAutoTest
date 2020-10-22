import json
from decimal import Decimal

from util import httpPost, httpGet, httpPut, operSql

SN ='http://192.168.104.132:8081'
SN1='http://192.168.104.132:8082'

# 获取k线接口
def kline_get(paralist):
    path='/gateway/market/data/kline/get'
    url=SN+path+'?contractId=%s&endTime=%s&startTime=%s&type=%s' %(paralist[0],paralist[1],paralist[2],paralist[3])
    resp = httpGet(url)
    print(resp)

#kline_get([1,1603247122000,1602160722000,60000])

# 获取所有交易对接口
def pairs_get():
    path='/gateway/common/pairs'
    url = SN1 + path
    resp = httpGet(url)
    #print(resp)
    return resp


# 新增交易对
def pairs_insert(paradic):
    path='/gateway/common/pairs'
    url = SN1 + path
    resp = httpPut(url,paradic)
    return resp

# 更新交易对（包含上下线）
def pairs_update(paradic):
    path='/gateway/common/pairs'
    url = SN1 + path
    resp = httpPost(url,paradic)
    return resp

# 交易对获取分页接口
def pairPageInfo_get(paralist):
    path='/gateway/common/pairPageInfo'
    url = SN1 + path +'?page=%s&size=%s&contractStatus=%s&name=%s' %(paralist[0],paralist[1],paralist[2],paralist[3])
    print(url)
    resp = httpGet(url)
    return resp

# 获取单个交易对信息
def pairs_one_get(id):
    path='/gateway/common/pairs/%s/SPOT' %(id)
    url = SN1 + path
    resp = httpGet(url)
    return resp


#创建合约参数
paradic1 = {
  "commodityId": 2,
  "currencyId": 1,
  "kycMatchLevel": 0,
  "limitMaxLevel": 10,
  "listPrice": 6,
  "listTime": 1603160722000,
  "lotSize": "0.01",
  "makerFeeRatio": "0.0003",
  "marketMaxLevel": 11,
  "maxNumOrders": 12,
  "priceLimitRate": 0.01,
  "priceTick": "0.0001",
  "sort": 2,
  "symbol": "USDT-CNYT",
  "takerFeeRatio": "0.0006",
  "type": "SPOT",
  #"contract_status":2
}
#kyc可交易等级，展示权重变更参数
paradic2 ={
  "contractId": 1,
  "applId": 1,
  "kycMatchLevel": 1,
  "sort": 0,
  "type": "SPOT",
  "updateType": 2,
  #"contract_status":2
}

paradic3 ={
  "contractId": 1,
  "applId": 1,
  "kycMatchLevel": 3,
  "limitMaxLevel": 3,
  "listPrice": 15,
  "listTime": 1603160722000,
  "lotSize": "0.00001",
  "makerFeeRatio": "0.01",
  "marketMaxLevel": 4,
  "maxNumOrders": 20,
  "priceLimitRate": 1.1,
  "priceTick": "0.01",
  "sort": 3,
  "takerFeeRatio": "0.0002",
  "type": "SPOT",
  "updateType": 3,
  "contract_status":2,
}
paradic4={
  "contractId": 11,
  "applId": 1,
  "contractStatus": 4,
  "type": "SPOT",
  "updateType": 1
}


#pairs_get()
#pairs_insert(paradic1)
pairs_update(paradic4)
#pairs_one_get(3)
#pairPageInfo_get([1,10,2,'BTC-USDT'])








