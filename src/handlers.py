import globals
import loggings
import time
import re
import configs

help_message = '''
/set user.name [value] - changing your user name
/set user.listen [true/false] - turning notifications on/off
/set user.send_log [true/false] - turning daily log sending on/off

/set await_time [int] - set the delay time when checking hosts

Use the following commands to view the set values:
/get user.name
/get user.listen
/get user.send_log
/get await_time

/add [ping/curl] [host] [name] [stop_after: true/false] [notify: true/false] [priority: integer]
/rm [ping/curl] [host]

/list [ping/curl] [ |W|E] - return list of hosts. W - falls count gt 1. E - falls count gt 3.

/version - return current version
'''

@globals.TELEBOT.message_handler(commands=['help'])
def help(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized')
        return

    try:
        globals.TELEBOT.reply_to(message, help_message)
    except Exception as e:
        globals.TELEBOT.reply_to(message, 'Something incomprehensible has happened..')

@globals.TELEBOT.message_handler(commands=['set'])
def set(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized')
        return

    message_text = re.sub(' +', ' ', message.text).strip().split(' ')
    try:
        commandlet = message_text[1]
        argument = message_text[2]
        configs.set_state(commandlet, message.from_user, argument)
    except IndexError as e:
        globals.TELEBOT.reply_to(message, 'Недостаточно аргументов!')
    except Exception as e:
        loggings.error(f'{message}: {e}')
        globals.TELEBOT.reply_to(message, e)

@globals.TELEBOT.message_handler(commands=['get'])
def get(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized')
        return

    message_text = re.sub(' +', ' ', message.text).strip().split(' ')
    try:
        commandlet = message_text[1]
        response = configs.get_state(commandlet, message.from_user)
        globals.TELEBOT.reply_to(message, response)
    except IndexError as e:
        globals.TELEBOT.reply_to(message, 'Недостаточно аргументов!')
    except Exception as e:
        loggings.error(f'{message}: {e}')
        globals.TELEBOT.reply_to(message, e)

@globals.TELEBOT.message_handler(commands=['add'])
def add(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized in config')
        return

    message_text = re.sub(' +', ' ', message.text).strip().split(' ')
    try:
        method = message_text[1]

        if method != 'ping' and method != 'curl':
            globals.TELEBOT.reply_to(message, 'Validate methods: ping or curl')
            return

        host = message_text[2]
        name = message_text[3]
        stop_after = message_text[4]
        notify = message_text[5]
        priority = message_text[6]

        configs.add_host(host, name, stop_after, notify, priority, method)
    except IndexError as e:
        globals.TELEBOT.reply_to(message, 'Недостаточно аргументов!')
    except Exception as e:
        loggings.error(f'{message}: {e}')
        globals.TELEBOT.reply_to(message, e)

@globals.TELEBOT.message_handler(commands=['rm'])
def rm(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized in config')
        return

    message_text = re.sub(' +', ' ', message.text).strip().split(' ')
    try:
        method = message_text[1]

        if method != 'ping' and method != 'curl':
            globals.TELEBOT.reply_to(message, 'Validate methods: ping or curl')
            return

        host = message_text[2]

        configs.rm_host(host, method)
    except IndexError as e:
        globals.TELEBOT.reply_to(message, 'Недостаточно аргументов!')
    except Exception as e:
        loggings.error(f'{message}: {e}')
        globals.TELEBOT.reply_to(message, e)

@globals.TELEBOT.message_handler(commands=['list'])
def list(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized in config')
        return

    message_text = re.sub(' +', ' ', message.text).strip().split(' ')
    try:
        method = message_text[1]

        if method != 'ping' and method != 'curl':
            globals.TELEBOT.reply_to(message, 'Validate methods: ping or curl')
            return

        falls_cnt_filter = 0
        if len(message_text) == 3:
            log_state = message_text[2]
            if log_state != 'W' and log_state != 'E':
                globals.TELEBOT.reply_to(message, 'Validate states: W or E')
                return
            if log_state == 'W':
                falls_cnt_filter = 1
            elif log_state == 'E':
                falls_cnt_filter = 3

        host_list = configs.host_list(method, falls_cnt_filter)
        globals.TELEBOT.reply_to(message, host_list)
    except IndexError as e:
        globals.TELEBOT.reply_to(message, 'Недостаточно аргументов!')
    except Exception as e:
        loggings.error(f'{message}: {e}')
        globals.TELEBOT.reply_to(message, e)

@globals.TELEBOT.message_handler(commands=['version'])
def list(message):

    if configs.validate_user(message.from_user) == False:
        globals.TELEBOT.reply_to(message, 'User is not authorized in config')
        return

    try:
        globals.TELEBOT.reply_to(message, f"{globals.CONF_VERSION} : {globals.LAST_UPDATES}")
    except IndexError as e:
        globals.TELEBOT.reply_to(message, 'Недостаточно аргументов!')
    except Exception as e:
        loggings.error(f'{message}: {e}')
        globals.TELEBOT.reply_to(message, e)

def poll_tg_bot():
    while True:
        try:
            globals.TELEBOT.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            loggings.error(e)
            time.sleep(5)
            continue