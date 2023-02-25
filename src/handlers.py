import globals

msg_help = '''
_List of all service commands_:

*/ping* - checking the stability of running monitoring
'''

msg_alive = 'I`m alive!!!'

@globals.TELEBOT.message_handler(commands=['help'])
def handle_help(message):
	globals.TELEBOT.reply_to(message, msg_help, parse_mode="Markdown")
 
@globals.TELEBOT.message_handler(commands=['ping'])
def handle_ping(message):
	globals.TELEBOT.reply_to(message, msg_alive)
 
globals.TELEBOT.polling()