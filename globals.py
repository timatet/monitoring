import os
from os import path
import shutil
import yaml

DATA_DIRECTORY = os.getenv('DATA_DIRECTORY', 'data')
CONFIG_FILE_NAME = os.getenv('CONFIG_FILE_NAME', 'config.yml')
CONFIG_FILE = f'{DATA_DIRECTORY}/{CONFIG_FILE_NAME}'
LOG_DIRECTORY = f'{DATA_DIRECTORY}/logs'

### Reading the configuration file
if path.isfile(CONFIG_FILE_NAME) and not path.isfile(CONFIG_FILE_NAME):
     shutil.copyfile(CONFIG_FILE_NAME, CONFIG_FILE)
try:
    f = open(CONFIG_FILE, 'r')
    config = yaml.load(f.read().replace('\t', '  '), Loader=yaml.FullLoader)
    f.close()
except:
    print(f"Configuration file error: {CONFIG_FILE}")
    exit(0)

CONF_VERSION = config['version']
CONF_TOKEN = config['token']
CONF_LOG_IMPORTANT = config['log_important']
CONF_AWAIT_TIME = config['await_time'] 
CONF_TG_CHATS = config['tg_chats']
CONF_IPS = config['ips']
CONF_DOMAINS = config['domains']
