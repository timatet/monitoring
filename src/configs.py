import os
import subprocess
from subprocess import DEVNULL, STDOUT
import json
import globals
import time
import loggings
import ruamel.yaml
import warnings

ADDRESATES = []
PING_LIST = []
CURL_LIST = []

UPDATED = ''

class Addresat :
    """
    Представляет получателя уведомлений.

    Атрибуты:
        id (str): Уникальный идентификатор чата.
        name (str): Имя пользователя.
        listen (bool): Флаг прослушивания уведомлений.
        send_log_every_day (bool): Флаг ежедневной отправки логов.
    """
    def __init__(self, id : str, name : str, listen : bool, send_log_every_day : bool):
        self.id = id
        self.name = name
        self.listen = listen
        self.send_log_every_day = send_log_every_day

    def to_json(self) -> dict:
        """
        Возвращает представление объекта Addresat в формате JSON-совместимого словаря.
        """
        return {
            'id': self.id,
            'name': self.name,
            'listen': self.listen,
            'send_log_every_day': self.send_log_every_day
        }

class Host :
    """
    Представляет хост, за которым необходимо следить.

    Атрибуты:
        name (str): Название хоста.
        host (str): Адрес хоста.
        check_method (str): Метод проверки (ping или curl).
        http_normal_code (str): Ожидаемый HTTP-код ответа.
        stop_after (bool): Останавливать проверку после падения.
        notify (bool): Отправлять уведомление.
        priority (int): Приоритет хоста.
    """
    def __init__(self, name : str, host : str, check_method : str, http_normal_code : str, stop_after : bool, notify : bool, priority : int):
        self.name = name
        self.host = host
        self.check_method = check_method
        self.http_normal_code = http_normal_code
        self.stop_after = stop_after
        self.notify = notify
        self.falls_cnt = 0
        self.fall_date = ''
        self.priority = priority

    def check(self) -> bool :
        """
        Выполняет проверку доступности хоста в зависимости от метода.
        Возвращает True, если хост доступен.
        """
        if self.check_method == "curl" :
            received_http_code = subprocess.check_output(f"curl -skL -o /dev/null -w '%{{http_code}}' -m 1 {self.host} || echo ''", shell=True).decode('UTF-8')
            return received_http_code == self.http_normal_code
        elif self.check_method == "ping" :
            return os.system(f"ping -c 3 -W 0{globals.CONF_DELIMITER}1 -i 0{globals.CONF_DELIMITER}2 {self.host} >> /dev/null 2>&1") == 0

    def to_json(self) -> dict:
        """
        Возвращает представление объекта Host в формате JSON-совместимого словаря.
        """
        return {
            'host': self.host,
            'name': self.name,
            'stop_after': self.stop_after,
            'notify': self.notify,
            'priority': self.priority,
            'http_normal_code': self.http_normal_code
        }

def get_hosts(conf_host_objs, check_method) -> list :
    """
    Создает список объектов Host из словаря конфигурации.

    Аргументы:
        conf_host_objs (list): Список словарей с данными хостов.
        check_method (str): Метод проверки (ping или curl).

    Возвращает:
        list: Список Host-объектов, отсортированных по приоритету.
    """
    hosts_list = []
    if conf_host_objs != None and len(conf_host_objs) > 0:
        for host in conf_host_objs:
            hosts_list.append(Host(
                name         = host['name'],
                host         = host['host'],
                check_method = check_method,
                http_normal_code = host['http_normal_code'] if 'http_normal_code' in host else '200',
                stop_after   = host['stop_after'] == 1,
                notify       = host['notify'],
                priority     = host['priority']
            ))
    sorted_by_priority = [check_method] + sorted(hosts_list, key=lambda x: x.priority, reverse=False)
    return sorted_by_priority

def get_receivers(conf_addr_objs) -> list :
    """
    Создает список объектов Addresat из конфигурации.

    Аргументы:
        conf_addr_objs (list): Список словарей с данными адресатов.

    Возвращает:
        list: Список Addresat-объектов.
    """
    addr_list = []
    for tg_chat in conf_addr_objs:
        addr_list.append(Addresat(
            id       = tg_chat['id'],
            name     = tg_chat['name'],
            listen   = tg_chat['listen'],
            send_log_every_day = tg_chat['send_log_every_day']
        ))
    return addr_list

@warnings.deprecated()
def strip_python_tags(s : str):
    """
    Удаляет теги YAML, начинающиеся на '!!python/'.

    Аргументы:
        s (str): YAML-строка.

    Возвращает:
        str: Очищенная строка YAML.
    """
    result = []
    for line in s.splitlines():
        idx = line.find("!!python/")
        if idx > -1:
            line = line[:idx]
        result.append(line)
    return '\n'.join(result)

class AppConfig :
    """
    Представляет основную конфигурацию приложения.

    Атрибуты:
        token (str): Токен телеграм-бота.
        log_important (bool): Важные логи.
        await_time (int): Время ожидания.
        tg_chats (list): Список адресатов.
        ping (list): Список хостов с методом ping.
        domains (list): Список хостов с методом curl.
    """
    def __init__(self, config_json : any):
        self.token = config_json['token']
        self.log_important = config_json['log_important']
        self.await_time = config_json['await_time']
        self.tg_chats = get_receivers(config_json['tg_chats'])
        self.ping = get_hosts(config_json['ping'], 'ping')
        self.domains = get_hosts(config_json['domains'], 'curl')

    def to_json(self) -> dict:
        """
        Возвращает представление объекта AppConfig в формате JSON-совместимого словаря.
        """
        return {
            'token': self.token,
            'log_important': self.log_important,
            'await_time': self.await_time,
            'tg_chats': self.tg_chats,
            'ping': json.dumps(self.ping),
            'domains': json.dumps(self.domains)
        }

def update_date():
    """
    Получает дату последнего изменения конфигурационного файла.

    Возвращает:
        str: Дата последнего изменения.
    """
    return time.ctime(os.path.getmtime(globals.CONFIG_FILE))

def configure_config():
    """
    Загружает и инициализирует глобальные переменные из конфигурационного файла.
    """
    global UPDATED
    if UPDATED != '':
        globals.read_config()

    global ADDRESATES
    ADDRESATES = get_receivers(globals.CONF_TG_CHATS)

    global PING_LIST
    PING_LIST = get_hosts(globals.CONF_PING, 'ping')

    global CURL_LIST
    CURL_LIST = get_hosts(globals.CONF_CURL, 'curl')

    UPDATED = update_date()

def check_config_update():
    """
    Проверяет, обновлялся ли конфигурационный файл.<br>
    При обновлении повторно загружает конфигурацию и уведомляет получателей.
    """
    if UPDATED != update_date():
        configure_config()
        loggings.info('Config updated.')
        for addresat in ADDRESATES:
            globals.TELEBOT.send_document(addresat.id, open(globals.CONFIG_FILE,"rb"), caption = 'Config updated.')

def set_state(state, addresat, value):
    """
    Обновляет значение параметра в конфигурационном файле для пользователя.

    Аргументы:
        state (str): Имя параметра.
        addresat (Addresat): Объект пользователя.
        value (str): Новое значение.
    """
    yaml = ruamel.yaml.YAML()
    with open(globals.CONFIG_FILE) as f:
        config = yaml.load(f)

    if state == 'user.name':
        for conf_elem in config['tg_chats']:
            if conf_elem['id'] == addresat.id:
                conf_elem['name'] = value
                break
    elif state == 'user.listen':
        for conf_elem in config['tg_chats']:
            if conf_elem['id'] == addresat.id:
                _value = eval(value.lower().capitalize())
                if _value == True or _value == False:
                    conf_elem['listen'] = _value
                else:
                    raise Exception("Values for 'user.listen' must be true or false")
                break
    elif state == 'user.send_log':
        for conf_elem in config['tg_chats']:
            if conf_elem['id'] == addresat.id:
                _value = eval(value.lower().capitalize())
                if _value == True or _value == False:
                    conf_elem['send_log_every_day'] = _value
                else:
                    raise Exception("Values for 'user.send_log' must be true or false")
                break
    elif state == 'await_time':
        config['await_time'] = int(value)
    else:
        raise Exception("Bad command! ")

    with open(globals.CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)

def get_state(state, addresat):
    """
    Получает значение параметра из конфигурационного файла для пользователя.

    Аргументы:
        state (str): Имя параметра.
        addresat (Addresat): Объект пользователя.

    Возвращает:
        любое: Значение параметра.
    """
    yaml = ruamel.yaml.YAML()
    with open(globals.CONFIG_FILE) as f:
        config = yaml.load(f)

    if state == 'user.name':
        for conf_elem in config['tg_chats']:
            if conf_elem['id'] == addresat.id:
                return conf_elem['name']
    elif state == 'user.listen':
        for conf_elem in config['tg_chats']:
            if conf_elem['id'] == addresat.id:
                return conf_elem['listen']
    elif state == 'user.send_log':
        for conf_elem in config['tg_chats']:
            if conf_elem['id'] == addresat.id:
                return conf_elem['send_log_every_day']
    elif state == 'await_time':
        return config['await_time']
    else:
        raise Exception("Bad command!")

def is_ip(address):
    """
    Проверяет, является ли адрес IP-адресом.

    Аргументы:
        address (str): Адрес для проверки.

    Возвращает:
        bool: True, если это IP.
    """
    return address.replace('.', '').isnumeric()

def is_registered(domain_name):
    """
    Проверяет, зарегистрировано ли доменное имя (наличие точки).

    Аргументы:
        domain_name (str): Домен для проверки.

    Возвращает:
        bool: True, если домен зарегистрирован.
    """
    return '.' in domain_name

def add_host(_host, _name, _stop_after, _notify, _priority, method):
    """
    Добавляет новый хост в конфигурацию.

    Аргументы:
        _host (str): Адрес хоста.
        _name (str): Имя хоста.
        _stop_after (str): Флаг остановки после падения.
        _notify (str): Флаг уведомления.
        _priority (str): Приоритет хоста.
        method (str): Метод проверки (ping или curl).

    Исключения:
        Exception: Если значения параметров некорректны.
    """
    yaml = ruamel.yaml.YAML()
    with open(globals.CONFIG_FILE) as f:
        config = yaml.load(f)

    exception_list = []

    if is_ip(_host) == False and is_registered(_host) == False:
        exception_list.append(f"Value {_host} for 'host' must be ip or registered domain")

    _value = eval(_stop_after.lower().capitalize())
    if _value != True and _value != False:
        exception_list.append(f"Value {_stop_after} for 'stop_after' must be true or false")

    _value = eval(_notify.lower().capitalize())
    if _value != True and _value != False:
        exception_list.append(f"Value {_notify} for 'notify' must be true or false")

    try:
        int(_priority)
    except:
        exception_list.append(f"Value {_priority} for 'priority' must be integer")

    if len(exception_list) > 0:
        raise Exception('\n'.join(exception_list))

    _host = dict([('host', _host), ('name', _name), ('stop_after', eval(_stop_after.lower().capitalize())), ('notify', eval(_notify.lower().capitalize())), ('priority', int(_priority))])
    if config[method] != None:
        config[method].append(_host)
    else:
        config[method] = [_host]

    with open(globals.CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)

def rm_host(host_name, method):
    """
    Удаляет хост из конфигурации по имени.

    Аргументы:
        host_name (str): Адрес хоста.
        method (str): Метод проверки.

    Исключения:
        Exception: Если хост не найден.
    """
    yaml = ruamel.yaml.YAML()
    with open(globals.CONFIG_FILE) as f:
        config = yaml.load(f)

    removed = False
    if config[method] != None:
        for idx, conf_elem in enumerate(config[method]):
            if conf_elem['host'] == host_name:
                del config[method][idx]
                removed = True
                break

    if removed == False:
        raise Exception('Host name not found in config')

    with open(globals.CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)

def host_list(method, falls_cnt_filter = 0):
    """
    Возвращает строку с информацией о хостах для указанного метода.

    Аргументы:
        method (str): Метод (ping или curl).
        falls_cnt_filter (int): Минимальное количество падений для отображения.

    Возвращает:
        str: Список хостов.
    """
    response = []

    if method == 'ping':
        hosts = PING_LIST[1:]
    else:
        hosts = CURL_LIST[1:]

    hosts = filter(lambda host: host.falls_cnt >= falls_cnt_filter, hosts)

    for host in hosts:
        response.append(
            f"{host.host}:\n\t\tName: {host.name}" +
            f"\n\t\tStop after: {host.stop_after}" +
            f"\n\t\tNotify: {host.notify}" +
            f"\n\t\tPriority: {host.priority}" +
            (f"\n\t\tFalls: {host.falls_cnt}" if falls_cnt_filter > 0 else "") +
            (f"\n\t\tLast fall date: {host.fall_date}" if falls_cnt_filter > 0 else "")
        )

    _response = '\n'.join(response)
    if _response == '':
        _response = 'The host list is empty!'
    return _response

def validate_user(addresat):
    """
    Проверяет, есть ли пользователь в конфигурации.

    Аргументы:
        addresat (Addresat): Проверяемый пользователь.

    Возвращает:
        bool: True, если пользователь найден.
    """
    yaml = ruamel.yaml.YAML()
    with open(globals.CONFIG_FILE) as f:
        config = yaml.load(f)

    for conf_elem in config['tg_chats']:
        if conf_elem['id'] == addresat.id:
            return True
    return False