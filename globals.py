import os
from os import path
import shutil
import yaml

### Edited before the deployment
CONF_VERSION = '1.0.4'
LAST_UPDATES = '''
- Added the ability to disable hosts alerts
- Notifications about new versions
- Addressees' names and so on..
'''

DATA_DIRECTORY = os.getenv('DATA_DIRECTORY', 'data')
CONFIG_FILE_NAME = os.getenv('CONFIG_FILE_NAME', 'config.yml')
CONFIG_FILE = f'{DATA_DIRECTORY}/{CONFIG_FILE_NAME}'
FILE_VERSION = f'{DATA_DIRECTORY}/version'
LOG_DIRECTORY = f'{DATA_DIRECTORY}/logs'

### Reading the configuration file
if path.isfile(CONFIG_FILE_NAME) and not path.isfile(CONFIG_FILE):
     shutil.copyfile(CONFIG_FILE_NAME, CONFIG_FILE)
try:
    f = open(CONFIG_FILE, 'r')
    config = yaml.load(f.read().replace('\t', '  '), Loader=yaml.FullLoader)
    f.close()
except:
    print(f"Configuration file error: {CONFIG_FILE}")
    exit(0)
    
### Checking version
IS_NEWVERSION = False
if not path.isfile(FILE_VERSION):
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

CONF_TOKEN = config['token']
CONF_LOG_IMPORTANT = config['log_important']
CONF_AWAIT_TIME = config['await_time'] 
CONF_TG_CHATS = config['tg_chats']
CONF_IPS = config['ips']
CONF_DOMAINS = config['domains']