import os
from time import sleep
import datetime
import subprocess
import globals
import loggings
import configs

### Defining local variables
loggings.info(f"A new session has been started. Service version: {globals.CONF_VERSION}")

prev_hosts_down = 0
cur_hosts_down  = 0     
keep_logging = True

def monitoring(hosts_list) :
    global prev_hosts_down
    global cur_hosts_down
    global keep_logging
    
    if keep_logging:
        loggings.info(f"{hosts_list[0]}: Checking...")
    for host in hosts_list[1:] :
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
                    msg = f"{hosts_list[0]}: '{host.name}' is unavailable"
                    loggings.info(msg)
                    keep_logging = True
                    for addresat in configs.ADDRESATES:
                        if host.notify and addresat.listen:
                            globals.TELEBOT.send_message(addresat.id, msg)
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
                    msg = f"{hosts_list[0]}: '{host.name}' was unavailable for " + delta.split(".")[0]
                    loggings.info(msg)
                    for addresat in configs.ADDRESATES:
                        if host.notify and addresat.listen:
                            globals.TELEBOT.send_message(addresat.id, msg)
                        keep_logging = True
                    host.otval_date = ""
                except:
                    loggings.error("JOPA")
                    keep_logging = True
    prev_hosts_down = prev_hosts_down + 1 if cur_hosts_down > 0 else 0
    cur_hosts_down = 0

configs.configure_config()
loggings.configure_logger()

hello_msg = ''
if globals.IS_NEWVERSION:
    hello_msg = f'''
    
Service update! New version is *v{globals.CONF_VERSION}*.
{globals.LAST_UPDATES}
_We send the file with the current configuration below:_
'''
    
for addresat in configs.ADDRESATES:
    if addresat.listen:
        globals.TELEBOT.send_message(addresat.id, f"Hi, *{addresat.name}*! Monitoring started! {hello_msg}", parse_mode="Markdown")
        if globals.IS_NEWVERSION:
            globals.TELEBOT.send_document(addresat.id, open(globals.CONFIG_FILE,"rb"))
loggings.info(f'Monitoring started for TG addresats {[(addresat.name, addresat.id) for addresat in configs.ADDRESATES if addresat.listen]}')

while(True) :
    monitoring(configs.PING_LIST)
    monitoring(configs.CURL_LIST)
    loggings.check_dates()
    configs.check_config_update()
    sleep(globals.CONF_AWAIT_TIME)