import os
import subprocess
import json
import globals
import time
import loggings

ADDRESATES = []
PING_LIST = []
CURL_LIST = []

UPDATED = ''

class Addresat :
    def __init__(self, id : str, name : str, listen : bool, send_log_every_day : bool):
        self.id = id
        self.name = name
        self.listen = listen
        self.send_log_every_day = send_log_every_day
        
    def to_json(self) -> dict: 
        return {
            'id': self.id,
            'name': self.name,
            'listen': self.listen,
            'send_log_every_day': self.send_log_every_day
        }
    
class Host :   
    def __init__(self, name : str, host : str, check_method : str, http_normal_code : str, stop_after : bool, notify : bool, priority : int):
        self.name = name
        self.host = host
        self.check_method = check_method
        self.http_normal_code = http_normal_code
        self.stop_after = stop_after
        self.notify = notify
        self.otval_cnt = 0
        self.otval_date = ''
        self.priority = priority
    
    def check(self) -> bool :
        if self.check_method == "curl" :
            received_http_code = subprocess.check_output(f"curl -skL -o /dev/null -w '%{self.http_normal_code}' -m 1 {self.host} || echo ''", shell=True).decode('UTF-8')
            return received_http_code == self.http_normal_code
        elif self.check_method == "ping" :
            return os.system(f"ping -c 3 -W 0{globals.CONF_DELIMITER}1 -i 0{globals.CONF_DELIMITER}2 {self.host} >> /dev/null") == 0
        
    def to_json(self) -> dict: 
        return {
            'host': self.host,
            'name': self.name,
            'stop_after': self.stop_after,
            'notify': self.notify,
            'priority': self.priority,
            'http_normal_code': self.http_normal_code
        }

def get_hosts(conf_host_objs, check_method) -> list :
    hosts_list = []
    if conf_host_objs != None and len(conf_host_objs) > 0:
        for host in conf_host_objs:     
            hosts_list.append(Host(
                name         = host['name'],
                host         = host['host'],
                check_method = check_method,
                http_normal_code = host['http_normal_code'] if 'http_normal_code' in host else '',
                stop_after   = host['stop_after'] == 1,
                notify       = host['notify'],
                priority     = host['priority']
            ))
    sorted_by_priority = [check_method] + sorted(hosts_list, key=lambda x: x.priority, reverse=False)
    return sorted_by_priority

def get_receivers(conf_addr_objs) -> list :  
    addr_list = []  
    for tg_chat in conf_addr_objs:
        addr_list.append(Addresat(
            id       = tg_chat['id'],
            name     = tg_chat['name'],
            listen   = tg_chat['listen'],
            send_log_every_day = tg_chat['send_log_every_day']
        ))  
    return addr_list

def strip_python_tags(s : str):
    result = []
    for line in s.splitlines():
        idx = line.find("!!python/")
        if idx > -1:
            line = line[:idx]
        result.append(line)
    return '\n'.join(result)

class AppConfig :    
    def __init__(self, config_json : any):
        self.token = config_json['token']
        self.log_important = config_json['log_important']
        self.await_time = config_json['await_time']
        self.tg_chats = get_receivers(config_json['tg_chats'])
        self.ping = get_hosts(config_json['ping'], 'ping')
        self.domains = get_hosts(config_json['domains'], 'curl')
        
    def to_json(self) -> dict: 
        return {
            'token': self.token,
            'log_important': self.log_important,
            'await_time': self.await_time,
            'tg_chats': self.tg_chats,
            'ping': json.dumps(self.ping),
            'domains': json.dumps(self.domains)
        }
        
def update_date():
    return time.ctime(os.path.getmtime(globals.CONFIG_FILE))
        
def configure_config() :
    global UPDATED
    if UPDATED != '':
        globals.read_config()
    
    global ADDRESATES
    ADDRESATES = get_receivers(globals.CONF_TG_CHATS)
    
    global PING_LIST
    PING_LIST = get_hosts(globals.CONF_PING, 'ping')
    
    global CURL_LIST
    CURL_LIST = get_hosts(globals.CONF_CURL, 'curl')
    
    UPDATED = update_date()
    
def check_config_update() :
    if UPDATED != update_date() :
        configure_config()
        loggings.info('Config updated.')
        for addresat in ADDRESATES:
            globals.TELEBOT.send_document(addresat.id, open(globals.CONFIG_FILE,"rb"), caption = 'Config updated.')