import time
import market
import telegram
import requests
from datetime import datetime

old_ip = "18.119.131.2"

curr_position = 0;
last_loop_time = time.localtime();

bot = telegram.Bot(token='1777908508:AAH_L-k9m8xAdBzSXNPncGnVCidOHZEt-SM')
updates = bot.getUpdates();
my_bot_id = 1836873714;
bot.sendMessage(chat_id=my_bot_id, text = "KPSTB_EMA (GAP=0.3) Started");
print("KPSTB_EMA (GAP=0.3) Started");

while True:
    sec = time.localtime().tm_sec;
    if(sec==0) :
        break;
    else :
        print("Wait for HH:MM:00 (curr="+str(sec)+")");
        time.sleep(1);

print("load kimp record started");
market.init_kimp_record();
print("load kimp record done");

while True:
    curr_ip = requests.get("http://jsonip.com").json()['ip'];
    curr_loop_time = time.localtime();
    
    if(curr_ip != old_ip) :
        bot.sendMessage(chat_id=my_bot_id, text="KPSTB_EMA: IP Changed!");
        print("IP Changed!");
        while True:
            bot.sendMessage(chat_id=my_bot_id, text="KPSTB_EMA: IP Changed!");
            time.sleep(60*10);
    else :
        market.update_market_price();
        kimp_buy = market.get_kimp_buy();
        kimp_sell = market.get_kimp_sell();
        kimp = (kimp_buy + kimp_sell)/2;
        ema_24h = market.get_ema24h(kimp);
        upthld = ema_24h + 0.3;
        dnthld = ema_24h - 0.3;
        
        if(kimp_sell > upthld) :
            if(curr_position!=0) :
                bot.sendMessage(chat_id=my_bot_id, text = ("KPSTB_EMA: execute_sell - \nkimp="+str(kimp)+"\nema="+str(ema_24h)));
                print("KPSTB: execute_sell - kimp="+str(kimp));
                market.execute_sell();
                curr_position = curr_position-1;
                bot.sendMessage(chat_id=my_bot_id, text = "KPSTB_EMA: SELL DONE!");
                print("KPSTB: SELL DONE!");
        elif(kimp_buy < dnthld) :
            if(curr_position<6) :
                bot.sendMessage(chat_id=my_bot_id, text = ("KPSTB_EMA: execute_buy - \nkimp="+str(kimp)+"\nema="+str(ema_24h)));
                print("KPSTB: execute_buy - kimp="+str(kimp));
                market.execute_buy();
                curr_position = curr_position+1;
                bot.sendMessage(chat_id=my_bot_id, text = "KPSTB_EMA: BUY DONE!");
                print("KPSTB: BUY DONE!");

        if(curr_loop_time.tm_min != last_loop_time.tm_min) :
            market.push_kimp(kimp);
            
            if(curr_loop_time.tm_min%10==0) :
                bot.sendMessage(chat_id=my_bot_id, text = ("KPSTB : still alive! - \nkimp="+str(kimp)+"\nema="+str(ema_24h)));
        
            if(curr_loop_time.tm_hour==0 and curr_loop_time.tm_min==0) :
                bot.sendMessage(chat_id=my_bot_id, text = "KPSTB : Save Kimp Record Started");
                market.save_kimp_record();
                bot.sendMessage(chat_id=my_bot_id, text = "KPSTB : Save Kimp Record Done");
        
        last_loop_time = curr_loop_time;
