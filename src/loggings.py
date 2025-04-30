import os
import logging
import globals
from datetime import date

def current_date():
    return date.today().strftime("%Y-%m-%d")

def get_logging_file():
    return f'{globals.LOG_DIRECTORY}/monitoring-{current_date()}.log'

def configure_logger() :
    '''
    Reconfiguration of the logger to make up-to-date parameters.
    '''
    _current_date = current_date()
    logging.info(f'Daily logger reconfiguration - {get_logging_file()}')
    if not os.path.exists(globals.LOG_DIRECTORY):
        os.makedirs(globals.LOG_DIRECTORY)
    logging.basicConfig(
        filename=get_logging_file(),
        filemode='a',
        format='%(asctime)s %(levelname)s\t:: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S%p',
        level=logging.DEBUG,
        force=True
    )

def error(log_msg):
    logging.error(log_msg)

def info(log_msg):
    logging.info(log_msg)

def warning(log_msg):
    logging.warning(log_msg)
