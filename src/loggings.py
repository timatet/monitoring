import os
import logging
import globals
import time

TIME_STYLE = "%Y-%m-%d"
CURRENT_DATA = time.strftime(TIME_STYLE)

def configure_logger() :
    """
    Создает файл журнала, если он не существует.
    """
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
    """
    Проверяет текущую дату и обновляет логгер, если дата изменилась.
    """
    global CURRENT_DATA
    last_data = time.strftime(TIME_STYLE)
    if CURRENT_DATA != last_data:
        CURRENT_DATA = last_data
        configure_logger()

def error(log_msg):
    """
    Записывает сообщение об ошибке в лог.
    """
    logging.error(log_msg)

def info(log_msg):
    """
    Записывает информационное сообщение в лог.
    """
    logging.info(log_msg)

def warning(log_msg):
    """
    Записывает предупреждающее сообщение в лог.
    """
    logging.warning(log_msg)
