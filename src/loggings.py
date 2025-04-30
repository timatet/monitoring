import os
import logging
import globals
from datetime import date

def current_date():
    return date.today().strftime("%Y-%m-%d")

CURRENT_DATA = current_date()

def configure_logger() :
    '''
    Reconfiguration of the logger to make up-to-date parameters.
    '''
    logging.info(f'Daily logger reconfiguration - {globals.LOG_DIRECTORY}/monitoring-{CURRENT_DATA}.log')
    if not os.path.exists(globals.LOG_DIRECTORY):
        os.makedirs(globals.LOG_DIRECTORY)
    logging.basicConfig(
        filename=f'{globals.LOG_DIRECTORY}/monitoring-{CURRENT_DATA}.log',
        filemode='a',
        format='%(asctime)s %(levelname)s\t:: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S%p',
        level=logging.DEBUG,
        force=True
    )

def check_dates() :
    global CURRENT_DATA
    _current_date = current_date()
    print(f'Checking dates {CURRENT_DATA} != {_current_date}?')
    if CURRENT_DATA != _current_date:
        CURRENT_DATA = _current_date
        configure_logger()

def error(log_msg):
    logging.error(log_msg)

def info(log_msg):
    logging.info(log_msg)

def warning(log_msg):
    logging.warning(log_msg)
