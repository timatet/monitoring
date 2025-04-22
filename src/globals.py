import os
import shutil
import yaml
import telebot

### Edited before the deployment
CONF_VERSION = '1.0.11 [fix]'
LAST_UPDATES = '''
- Исправлена ошибка в работе параметра stop\_after
- Version handler
'''

DATA_DIRECTORY = os.getenv('DATA_DIRECTORY', 'data')
CONFIG_FILE_NAME = os.getenv('CONFIG_FILE_NAME', 'config.yml')
CONFIG_FILE = f'{DATA_DIRECTORY}/{CONFIG_FILE_NAME}'
FILE_VERSION = f'{DATA_DIRECTORY}/version'
LOG_DIRECTORY = f'{DATA_DIRECTORY}/logs'

if 'TG_BOT_TOKEN' in os.environ:
    TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
else:
    print("Telegram bot token not specified")
    exit(0)

CONF_LOG_IMPORTANT = None
CONF_AWAIT_TIME = None
CONF_TG_CHATS = None
CONF_PING = None
CONF_CURL = None
CONF_DELIMITER = None

config = ''
def read_config() :
    global config

    ### Reading the configuration file
    if os.path.isfile(CONFIG_FILE_NAME) and not os.path.isfile(CONFIG_FILE):
        shutil.copyfile(CONFIG_FILE_NAME, CONFIG_FILE)
    try:
        f = open(CONFIG_FILE, 'r')
        config = yaml.load(f.read().replace('\t', '  '), Loader=yaml.FullLoader)
        f.close()

        global CONF_LOG_IMPORTANT, CONF_AWAIT_TIME, CONF_TG_CHATS, CONF_PING, CONF_CURL, CONF_DELIMITER
        CONF_LOG_IMPORTANT = config['log_important']
        CONF_AWAIT_TIME = config['await_time']
        CONF_TG_CHATS = config['tg_chats']
        CONF_PING = config['ping']
        CONF_CURL = config['curl']
        CONF_DELIMITER = config['delimiter']
    except Exception as e:
        print(e)
        print(f"Configuration file error: {CONFIG_FILE}")
        exit(0)

read_config()

### Checking version
IS_NEWVERSION = False
if not os.path.isfile(FILE_VERSION):
    vers_file = open(FILE_VERSION, 'x')
    vers_file.write(CONF_VERSION)
    IS_NEWVERSION = True
else:
    vers_file = open(FILE_VERSION, 'r+')
    last_v = vers_file.readline()

    if last_v != CONF_VERSION:
        vers_file.seek(0)
        vers_file.write(CONF_VERSION)
        vers_file.truncate()
        IS_NEWVERSION = True
vers_file.close()

TELEBOT = telebot.TeleBot(TG_BOT_TOKEN)