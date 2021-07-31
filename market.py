import ccxt
import pyupbit
import pprint
import requests
import time
from datetime import datetime

kimp_record = [0.1]*1440;
last_exchange = 1150;
exchange_timestamp = 0;

bi_order_buy_price  = 0;
bi_order_sell_price = 0;
ub_order_sell_price = 0;
ub_order_buy_price  = 0;

binance = ccxt.binance(config={
    'apiKey': '7PIXS6ISNkcn5auaiETj3T87xA50xKqcdejVdC1oBsI8Y4Anf9akAbxtnnjFwQ5K',
    'secret': 'nAUWMjkzTaeh5hd3OYbDbMuz2FCgMA7F34edw6ZRq8C3tdjpIrcE3GVoPFpyYS4e',
    'enableRateLimit': True, 
    'options': {
        'defaultType': 'future'
    }
})
upbit = pyupbit.Upbit('TcEx3Bi4LLgbiJFML448EBvAuSE1VxhHtaLdNTgv', 'DHTK6xsG116V26a84Hu4flW5Cr370dDgZR1xVnxl')



def execute_buy() :
    # short binance
    order = binance.create_limit_sell_order(
        symbol="BTC/USDT", 
        amount=0.005, 
        price=bi_order_sell_price
        #price=binance.fetch_order_book('BTC/USDT')['bids'][2][0]
    )
    # buy upbit
    upbit.buy_limit_order("KRW-BTC", ub_order_buy_price, 0.005);
    #upbit.buy_limit_order("KRW-BTC", pyupbit.get_orderbook("KRW-BTC")[0]['orderbook_units'][2]['ask_price'], 0.05);
    #pyupbit.get_orderbook("KRW-BTC")[0]['orderbook_units'][1]['ask_price']
    

def execute_sell() :
    # short binance
    order = binance.create_limit_buy_order(
        symbol="BTC/USDT", 
        amount=0.005, 
        price=bi_order_buy_price
        #price=binance.fetch_order_book('BTC/USDT')['asks'][2][0]
    )
    # buy upbit
    upbit.sell_limit_order("KRW-BTC", ub_order_sell_price, 0.005);
    #upbit.sell_limit_order("KRW-BTC", pyupbit.get_orderbook("KRW-BTC")[0]['orderbook_units'][2]['bid_price'], 0.05);
    #pyupbit.get_orderbook("KRW-BTC")[0]['orderbook_units'][1]['ask_price']

def get_exchange():
    global exchange_timestamp
    global last_exchange
    if(exchange_timestamp < time.mktime(time.localtime())-60) :
        req = 'https://exchange.jaeheon.kr:23490/query/USDKRW'
        res = requests.get(req)
        try:
            jres = res.json()
        except:
            res = requests.get(req)
            jres = res.json()
        update = jres['update']
        USDKRW = jres['USDKRW']
        #[Price, Change, ChangePercent, PreviousClose, Open, DayLow, DayHigh]
        date = datetime.fromtimestamp(int(update/1000))
        ret = USDKRW[0]
        
        exchange_timestamp = time.mktime(time.localtime());
        last_exchange = ret;
        print("exchange updated");
        
        return ret
    else :
        return last_exchange;

def get_kimp() :
    ub_price = pyupbit.get_current_price("KRW-BTC");
    bn_price = binance.fetch_ticker('BTC/USDT')['close'];
    bn_krw   = bn_price * get_exchange();
    return ((ub_price-bn_krw)/ub_price)*100;

def get_kimp_buy() :
    global bi_order_buy_price;
    global ub_order_sell_price;
    global bi_order_buy_price;
    global ub_order_sell_price;
    
    ub_price = ub_order_buy_price;
    bn_price = bi_order_sell_price;
    bn_krw   = bn_price * get_exchange();
    
    return ((ub_price-bn_krw)/ub_price)*100;

def get_kimp_sell() :
    global bi_order_buy_price;
    global ub_order_sell_price;
    global bi_order_buy_price;
    global ub_order_sell_price;
    
    ub_price = ub_order_sell_price;
    bn_price = bi_order_buy_price;
    bn_krw   = bn_price * get_exchange();
    return ((ub_price-bn_krw)/ub_price)*100;

def update_market_price() :
    global bi_order_buy_price;
    global bi_order_sell_price;
    global ub_order_buy_price;
    global ub_order_sell_price;
    
    bn = binance.fetch_order_book('BTC/USDT');
    ub = pyupbit.get_orderbook("KRW-BTC");
    
    bi_order_buy_price  = bn['bids'][2][0];
    bi_order_sell_price = bn['asks'][2][0];
    ub_order_buy_price  = ub[0]['orderbook_units'][2]['ask_price'];
    ub_order_sell_price = ub[0]['orderbook_units'][2]['bid_price'];
    
    

def print_market_prices() :
    global bi_order_buy_price;
    global bi_order_sell_price;
    global ub_order_sell_price;
    global ub_order_buy_price;
    
    print(bi_order_buy_price);
    print(bi_order_sell_price);
    print(ub_order_sell_price);
    print(ub_order_buy_price);
    
def init_kimp_record() :
    exchange = get_exchange();
    file_out = open("temp_record.log", "w");
    for iHH in range(24) :
        str_to = datetime.fromtimestamp(time.mktime(time.localtime())-3600*(23-iHH));
        str_to_2 = datetime.fromtimestamp(time.mktime(time.localtime())-3600*(24-iHH));
        print(str_to);
        df = pyupbit.get_ohlcv(ticker="KRW-BTC", interval="minute1", count=60, to=str_to);
        ohlcvs = binance.fetch_ohlcv(symbol='BTC/USDT', timeframe='1m', since=int(datetime.strptime(str(str_to_2), "%Y-%m-%d %H:%M:%S").timestamp()*1000), limit=60)
        for iMM in range(60) :
            ub_price = df.close[iMM];
            bn_price = ohlcvs[iMM][4];
            bn_krw   = bn_price * exchange;
            kimp_record[iHH*60+iMM] = ((ub_price-bn_krw)/ub_price)*100;
            file_out.write(str(df.index[iMM]));
            file_out.write(",");
            file_out.write(str(df.open[iMM]));
            file_out.write(",");
            file_out.write(str(df.high[iMM]));
            file_out.write(",");
            file_out.write(str(df.low[iMM]));
            file_out.write(",");
            file_out.write(str(df.close[iMM]));
            file_out.write(",,");
            file_out.write(datetime.fromtimestamp(ohlcvs[iMM][0]/1000).strftime('%Y-%m-%d %H:%M:%S'));
            file_out.write(str(ohlcvs[iMM][1]));
            file_out.write(",");
            file_out.write(str(ohlcvs[iMM][2]));
            file_out.write(",");
            file_out.write(str(ohlcvs[iMM][3]));
            file_out.write(",");
            file_out.write(str(ohlcvs[iMM][4]));
            file_out.write("\n");
            

def save_kimp_record() :
    today = time.localtime();
    file_out = open("./KIMP_RECORD/kimp_record_{yy}_{mm}_{dd}.csv".format(yy=today.tm_year, mm=today.tm_mon, dd=today.tm_mday), "w");
    
    
    print(datetime.fromtimestamp(time.mktime(time.localtime())-3600*(23-23-9)-60*(59-59)));
    
    for iHH in range(24) :
        for iMM in range(60) :
            str_to = datetime.fromtimestamp(time.mktime(time.localtime())-3600*(23-iHH-9)-60*(59-iMM));
            file_out.write(str(str_to));
            file_out.write(",");
            file_out.write(str(kimp_record[iHH*60+iMM]));
            file_out.write("\n");

def push_kimp(curr_kimp) :
    #print("kimp_record[0] = " + str(kimp_record[0]));
    for i in range(1440-1) :
        kimp_record[i] = kimp_record[i+1];
    kimp_record[1440-1] = curr_kimp;

def get_ema24h(curr_kimp) :
    return (sum(kimp_record[1:1440-1])+curr_kimp)/1440;
        
        
#init_kimp_record();
#print(get_ema24h(kimp_record[1440-1]));
#save_kimp_record();
