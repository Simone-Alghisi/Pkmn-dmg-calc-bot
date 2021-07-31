from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os
import bot.commands
import bot.error

load_dotenv()
TOKEN = os.getenv('TOKEN')
PORT = int(os.environ.get('PORT', os.getenv('PORT')))

def main():
  updater = Updater(TOKEN)
  
  updater.dispatcher.add_error_handler(bot.error.error_handler)

  commands = bot.commands.get_commands()
  for command_name, command_function in commands:
    updater.dispatcher.add_handler(CommandHandler(command_name, command_function))

  conversations = bot.commands.get_conversations()
  for conv_handler in conversations:
    updater.dispatcher.add_handler(conv_handler)

  #TODO needs to be commented
  #updater.start_polling() # for testing only

  #TODO remove comments from this
  #
  updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
  updater.bot.setWebhook('https://evening-falls-15281.herokuapp.com/' + TOKEN)
  #

  updater.idle()

if __name__ == '__main__':
  if TOKEN:
    main()
  else:
    print('Lmao') #best error message ever