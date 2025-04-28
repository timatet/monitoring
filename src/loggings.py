import os
import logging
import globals
import time

TIME_STYLE = "%Y-%m-%d"
CURRENT_DATA = time.strftime(TIME_STYLE)

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
    last_data = time.strftime(TIME_STYLE)
    print(f'Checking dates {CURRENT_DATA} != {last_data}?')
    if CURRENT_DATA != last_data:
        CURRENT_DATA = last_data
        configure_logger()

def error(log_msg):
    logging.error(log_msg)

def info(log_msg):
    logging.info(log_msg)

def warning(log_msg):
    logging.warning(log_msg)
