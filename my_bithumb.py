
import time
from datetime import datetime, timedelta
import requests
import json
import datetime
from datetime import datetime, timedelta

import pybithumb
import config
from my_util import print_log

bithumb = None
hold_position = 0
hold_krw = 0

market_price = 0
ask_price = 0
bid_price = 0

orders = []
order_details = {}

candle = []

def initialize() :
    global bithumb
    global api
    api_key = config.get_config('BT_API_KEY')
    secret_key = config.get_config('BT_SECRET_KEY')
    bithumb = pybithumb.Bithumb(api_key, secret_key)
    return 0

test_candle = []

def init_test_candle(n_day=1) :
    global market_price
    global test_candle
    now = datetime.now() + timedelta(hours=9)
    for iHH in range(0, int(24*n_day), 3) :
        if iHH%24 == 0 :
            print(iHH/24)
        past_time = now - timedelta(hours=iHH)
        formatted_time = past_time.strftime("%y-%m-%dT%H:%M")
        url = "https://api.bithumb.com/v1/candles/minutes/1?market=KRW-USDT&count=180&to=20"+formatted_time
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        for iMM in range(180) :
            market_price = data[iMM]
            test_candle.append(get_kp())
    candle = list(reversed(test_candle))
    return 0


def candle_test() :
    now = datetime.now() + timedelta(hours=9)
    past_time = now - timedelta(hours=0)
    formatted_time = past_time.strftime("%y-%m-%dT%H:%M")
    url = "https://api.bithumb.com/v1/candles/minutes/1?market=KRW-USDT&count=180&to=20"+formatted_time
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    return data

def init_candle(n_day=1) :
    global market_price
    global candle
    now = datetime.now() + timedelta(hours=9)
    for iHH in range(0, int(24*n_day), 3) :
        if iHH%24 == 0 :
            print(iHH/24)
        past_time = now - timedelta(hours=iHH)
        formatted_time = past_time.strftime("%y-%m-%dT%H:%M")
        url = "https://api.bithumb.com/v1/candles/minutes/1?market=KRW-USDT&count=180&to=20"+formatted_time
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        for iMM in range(180) :
            market_price = float(data[iMM]['trade_price'])
            candle.append(get_kp())
    candle = list(reversed(candle))
    update_market_price()
    update_candle(get_kp())
    return 0

def update_candle(kp) :
    candle.pop(0)
    candle.append(kp)
    return 0

def update_candle_tail(kp) :
    candle[-1] = kp
    return 0

def update_balance() :
    global hold_position
    global hold_krw
    balance = bithumb.get_balance('USDT')
    while balance==None :
        print('get_balance retry')
        balance = bithumb.get_balance('USDT')
    hold_position = balance[0]
    hold_krw = balance[2]
    return 0

def update_market_price() :
    global market_price
    market_price_pre = pybithumb.get_current_price('USDT')
    if market_price_pre != 0 and market_price_pre != None:
        market_price = market_price_pre
    return 0

def update_orderbook() :
    global ask_price
    global bid_price
    order_book = pybithumb.get_orderbook('USDT')
    while order_book == None :
        order_book = pybithumb.get_orderbook('USDT')
        print('pybithumb get_orderbook error, retry')
    ask_price = order_book['asks'][0]['price']
    bid_price = order_book['bids'][0]['price']
    return 0

def buy_limit_order(symbol, price, amount):
    print('buy_limit_order ' + str(price) + ' / ' + str(amount))
    order = bithumb.buy_limit_order(symbol, price, amount)
    #order = bithumb.buy_limit_order(symbol, price, 5)
    print(order)
    order_mod = (order[0], order[1], order[2], order[3], price)
    orders.append(order_mod)
    return 0

def sell_limit_order(symbol, price, amount):
    print('sell_limit_order ' + str(price) + ' / ' + str(amount))
    order = bithumb.sell_limit_order(symbol, price, amount)
    #order = bithumb.sell_limit_order(symbol, price, 5)
    print(order)
    order_mod = (order[0], order[1], order[2], order[3], price)
    orders.append(order_mod)
    return 0

def buy_market_order(symbol, amount):
    bithumb.buy_limit_order(symbol, ask_price, amount)
    return 0

def sell_market_order(symbol, amount):
    bithumb.sell_limit_order(symbol, bid_price, amount)
    return 0

def update_orders() :
    global order_details
    for order_id in order_details :
        if order_details[order_id]['data']['order_status'] != 'Pending' :
            for order in orders :
                if order[2] == order_id :
                    orders.remove(order)
    order_details = {}
    for order in orders :
        order_detail = bithumb.get_order_completed(order)
        order_details[order[2]] = order_detail
    return 0

def cancel_order(order_id) :
    for order in orders :
        if order[2] == order_id :
            bithumb.cancel_order((order[0], order[1], order[2], order[3]))
            orders.remove(order)
            return 0
    return 1

def get_kp() :
    kp = market_price
    return kp

def get_ma() :
    ma = round(sum(candle[-1440:])/1440, 3)
    return ma
