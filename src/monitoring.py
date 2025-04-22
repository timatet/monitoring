from time import sleep
import datetime
import threading
import globals
import loggings
import configs
import schedule
import time
import handlers

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

    host_idx = 0
    while host_idx in range(len(hosts_list[1:])) :
        if (not hosts_list[host_idx + 1].check()) :
            cur_hosts_down += 1
            if keep_logging:
                loggings.info(f"host.name : {hosts_list[host_idx + 1].name}, host.falls_cnt : {hosts_list[host_idx + 1].falls_cnt}, prev_hosts_down : {prev_hosts_down}, cur_hosts_down : {cur_hosts_down}")
                if globals.CONF_LOG_IMPORTANT:
                    keep_logging = False
            if (hosts_list[host_idx + 1].falls_cnt < 3 - (1 if (prev_hosts_down > hosts_list[host_idx + 1].falls_cnt) else 0)) : #если отвалился шлюз ближе, чем тот, который был раньше замечен
                hosts_list[host_idx + 1].falls_cnt += 1
                continue

            if (hosts_list[host_idx + 1].fall_date == "") :
                hosts_list[host_idx + 1].fall_date = datetime.datetime.now()
                try:
                    msg = f"{hosts_list[0]}: '{hosts_list[host_idx + 1].name}' is unavailable"
                    loggings.info(msg)
                    keep_logging = True
                    for addresat in configs.ADDRESATES:
                        if hosts_list[host_idx + 1].notify and addresat.listen:
                            globals.TELEBOT.send_message(addresat.id, msg)
                except Exception as e:
                    loggings.error(e)
                    keep_logging = True

            if hosts_list[host_idx + 1].stop_after :
                loggings.warning("BREAK")
                keep_logging = True
                break
        else :
            hosts_list[host_idx + 1].falls_cnt = 0
            if (hosts_list[host_idx + 1].fall_date != "") :
                try:
                    delta = str(datetime.datetime.now() - hosts_list[host_idx + 1].fall_date)
                    msg = f"{hosts_list[0]}: '{hosts_list[host_idx + 1].name}' was unavailable for " + delta.split(".")[0]
                    loggings.info(msg)
                    for addresat in configs.ADDRESATES:
                        if hosts_list[host_idx + 1].notify and addresat.listen:
                            globals.TELEBOT.send_message(addresat.id, msg)
                        keep_logging = True
                    hosts_list[host_idx + 1].fall_date = ""
                except Exception as e:
                    loggings.error(e)
                    keep_logging = True
        host_idx += 1
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

def send_log() :
    loggings.info('Every day log sending begin...')
    for addresat in configs.ADDRESATES:
        if addresat.send_log_every_day:
            globals.TELEBOT.send_document(addresat.id, open(f'{globals.LOG_DIRECTORY}/monitoring-{loggings.CURRENT_DATA}.log', 'rb'), caption = 'Sending logs for the past day')
    loggings.info('Every day log sending ended.')

schedule.every(1).day.at('23:59').do(send_log)

def pende_tasks() :
    while 1:
        schedule.run_pending()
        time.sleep(1)

sheduler_pending = threading.Thread(target=pende_tasks)
sheduler_pending.start()

tg_bot_polling = threading.Thread(target=handlers.poll_tg_bot)
tg_bot_polling.start()

while(True) :
    monitoring(configs.PING_LIST)
    monitoring(configs.CURL_LIST)
    loggings.check_dates()
    configs.check_config_update()
    sleep(globals.CONF_AWAIT_TIME)