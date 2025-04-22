import telebot
import socket
import globals

def check_telebot():
   """
   Проверяет подключение к Telegram Bot API.

   Возвращает:
         int: 0, если подключение успешно, 1 в противном случае.
   """
   try:
      me = globals.TELEBOT.get_me()
      return 0
   except telebot.apihelper.ApiException as e:
      print(f"Ошибка подключения к Telegram Bot API: {e}\n")
      return 1
   except Exception as e:
      print(f"Произошла неизвестная ошибка: {e}\n")
      return 1


if __name__ == "__main__":
   telebot_status = check_telebot()

   if telebot_status == 0:
      exit(0)
   else:
      exit(1)
