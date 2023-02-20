import os
from time import sleep
import telebot
import datetime
import subprocess
import globals
import loggings
    
class Host(object) :
    def __init__(self, name : str, address : str, check_method : str, http_code : str, stop_after : bool):
        self.name = name
        self.address = address
        self.check_method = check_method
        self.http_code = http_code
        self.otval_date = ""
        self.otval_cnt = 0
        self.stop_after = stop_after
    
    def check(self) -> bool :
        if self.check_method == "curl" :
            received_http_code = subprocess.check_output(f"curl -skL -o /dev/null -w '%{{http_code}}' -m 1 {self.address} || echo ''", shell=True).decode('UTF-8')
            return received_http_code == self.http_code
        elif self.check_method == "ping" :
            return os.system(f"ping -c 3 -W 0.1 -i 0.2 {self.address} >> /dev/null") == 0

### Defining local variables
loggings.info(f"A new session has been started. Service version: {globals.CONF_VERSION}")
await_time  = globals.CONF_AWAIT_TIME
bot         = telebot.TeleBot(globals.CONF_TOKEN)
addr_list   = []
hosts_list  = []
prev_hosts_down = 0
cur_hosts_down  = 0     
keep_logging = True

def get_receivers() :    
    for tg_chat in globals.CONF_TG_CHATS:
        if tg_chat['listen'] == 1:
            addr_list.append(
                tg_chat['id']
            )  

def get_hosts() :
    for ip in globals.CONF_IPS:     
        hosts_list.append(Host(
            name         = ip['name'],
            address      = ip['ip'],
            check_method = "ping",
            http_code    = "",
            stop_after   = ip['stop'] == 1
        ))
    
    for domain in globals.CONF_DOMAINS:
        hosts_list.append(Host(
            name         = domain['name'],
            address      = domain['domain'],
            check_method = "curl",
            http_code    = domain['http_normal_code'],
            stop_after   = domain['stop'] == 1
        ))

def monitoring() :
    global prev_hosts_down
    global cur_hosts_down
    global keep_logging

    
    if keep_logging:
        loggings.info(f"Checking...")
    for host in hosts_list :
        if (not host.check()) :
            cur_hosts_down += 1
            if keep_logging:
                loggings.info(f"host.name : {host.name}, host.otval_cnt : {host.otval_cnt}, prev_hosts_down : {prev_hosts_down}, cur_hosts_down : {cur_hosts_down}")
                if globals.CONF_LOG_IMPORTANT:
                    keep_logging = False
            if (host.otval_cnt < 3 - (1 if (prev_hosts_down > host.otval_cnt) else 0)) : #если отвалился шлюз ближе, чем тот, который был раньше замечен
                host.otval_cnt += 1
                continue
            
            if (host.otval_date == "") :
                host.otval_date = datetime.datetime.now()
                try:
                    loggings.info(f"{host.name} is unavailable")
                    keep_logging = True
                    for addresat in addr_list:
                        bot.send_message(addresat, f"{host.name} is unavailable")
                except:
                    loggings.error("JOPA")
                    keep_logging = True
             
            if host.stop_after :
                loggings.warning("BREAK")
                keep_logging = True
                break
        else :
            host.otval_cnt = 0
            if (host.otval_date != "") :
                try:
                    delta = str(datetime.datetime.now() - host.otval_date)
                    for addresat in addr_list:
                        bot.send_message(addresat, f"{host.name} was unavailable for " + delta.split(".")[0])
                        keep_logging = True
                    host.otval_date = ""
                except:
                    loggings.error("JOPA")
                    keep_logging = True
    prev_hosts_down = prev_hosts_down + 1 if cur_hosts_down > 0 else 0
    cur_hosts_down = 0
    
get_receivers() 
get_hosts()
loggings.configure_logger()
for addresat in addr_list:
    bot.send_message(addresat, "Monitoring started")

while(True) :
    monitoring()
    loggings.check_dates()
    sleep(await_time)