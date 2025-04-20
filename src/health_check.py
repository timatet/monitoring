import telebot
import socket
import globals

def check_network():
   try:
      socket.create_connection(("8.8.8.8", 53))
      return 0
   except OSError as e:
      print(f"Network error: {e}")
      return 1

def check_telebot():
   try:
      me = globals.telebot.get_me()
      print(f"Подключение успешно! Информация о боте: {me}")
      return 0
   except telebot.apihelper.ApiException as e:
      print(f"Ошибка подключения к Telegram Bot API: {e}")
      return 1
   except Exception as e:
      print(f"Произошла неизвестная ошибка: {e}")
      return 1


if __name__ == "__main__":
   network_status = check_network()
   telebot_status = check_telebot()

   if network_status == 0 and telebot_status == 0:
      exit(0)
   else:
      exit(1)
