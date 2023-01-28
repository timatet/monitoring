import os
from time import sleep
import telebot
import datetime
import subprocess
import yaml
import logging

CONFIG_FILE = 'config.yml'
logging.basicConfig(
    filename='monitoring.log', 
    filemode='a', 
    format='%(asctime)s %(levelname)s\t:: %(message)s', 
    datefmt='%m/%d/%Y %I:%M:%S%p', 
    level=logging.DEBUG
) 

try:
    f = open(CONFIG_FILE, 'r')
    config = yaml.load(f.read().replace('\t', '  '), Loader=yaml.FullLoader)
    f.close()
except:
    logging.error(f"Configuration file error: {CONFIG_FILE}")
    exit(0)
    
logging.info(f"A new session has been started. Service version: {config['version']}")
bot = telebot.TeleBot(config['token'])
addr_list = []
for tg_chat in config['tg_chats']:
    if tg_chat['listen'] == 1:
        addr_list.append(tg_chat['id'])
hosts_list = []
prev_hosts_down = 0
cur_hosts_down = 0


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
            return os.system(f"ping -c 3 -W 0,1 -i 0,2 {self.address} >> /dev/null") == 0
                    

def get_hosts() :
    for ip in config['ips']:     
        hosts_list.append(Host(
            name         = ip['name'],
            address      = ip['ip'],
            check_method = "ping",
            http_code    = "",
            stop_after   = ip['stop'] == 1
        ))
    
    for domain in config['domains']:
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

    logging.info(f"Checking...")
    for host in hosts_list :
        if (not host.check()) :
            cur_hosts_down += 1
            logging.info(f"host.name : {host.name}, host.otval_cnt : {host.otval_cnt}, prev_hosts_down : {prev_hosts_down}, cur_hosts_down : {cur_hosts_down}")
            if (host.otval_cnt < 3 - (1 if (prev_hosts_down > host.otval_cnt) else 0)) : #если отвалился шлюз ближе, чем тот, который был раньше замечен
                host.otval_cnt += 1
                continue
            
            if (host.otval_date == "") :
                host.otval_date = datetime.datetime.now()
                try:
                    logging.info(f"{host.name} is unavailable")
                    for addresat in addr_list:
                        bot.send_message(addresat, f"{host.name} is unavailable")
                except:
                    logging.error("JOPA")
             
            if host.stop_after :
                logging.warning("BREAK")
                break
        else :
            host.otval_cnt = 0
            if (host.otval_date != "") :
                try:
                    delta = str(datetime.datetime.now() - host.otval_date)
                    for addresat in addr_list:
                        bot.send_message(addresat, f"{host.name} was unavailable for " + delta.split(".")[0])
                    host.otval_date = ""
                except:
                    logging.error("JOPA")
    prev_hosts_down = prev_hosts_down + 1 if cur_hosts_down > 0 else 0
    cur_hosts_down = 0

get_hosts()
for addresat in addr_list:
    bot.send_message(addresat, "Monitoring started")

while(True) :
    monitoring()
    sleep(2)