from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler
from dotenv import load_dotenv
import os
import bot.commands
import bot.error
import argparse

load_dotenv()
TOKEN = os.getenv('TOKEN')
PORT = int(os.environ.get('PORT', os.getenv('PORT')))
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID')

def get_args():
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(
    prog='Pkmn-calc-dmg-bot',
    description='Telegram bot to calculate damage dealt by a move performed by a specific pkmn on another.',
  )
  parser.add_argument(
    '--debug-mode',
    action='store_true',
    required=False,
    default=False,
    help='Sets the bot in debug mode [default: False].',
  )

  return parser.parse_args()

def main():
  updater = Updater(TOKEN)
  
  updater.dispatcher.add_error_handler(bot.error.error_handler)

  args = get_args()
  if not args.debug_mode:
    commands = bot.commands.get_commands()
    for command_name, command_function in commands:
      updater.dispatcher.add_handler(CommandHandler(command_name, command_function))

    conversations = bot.commands.get_conversations()
    for conv_handler in conversations:
      updater.dispatcher.add_handler(conv_handler())
  else:
    commands = bot.commands.get_commands()
    for command_name, command_function in commands:
      updater.dispatcher.add_handler(CommandHandler(command_name, command_function, Filters.user(user_id=[int(DEVELOPER_CHAT_ID)])))

    conversations = bot.commands.get_conversations()
    for conv_handler in conversations:
      updater.dispatcher.add_handler(conv_handler(int(DEVELOPER_CHAT_ID)))

    updater.dispatcher.add_handler(MessageHandler(Filters.command&~Filters.user(user_id=[int(DEVELOPER_CHAT_ID)]), bot.commands.debug))

  #TODO needs to be commented
  #updater.start_polling() # for testing only

  #TODO remove comments from this
  #
  updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
  updater.bot.setWebhook(os.getenv('WEBHOOK'))
  #

  updater.idle()

if __name__ == '__main__':
  if TOKEN:
    main()
  else:
    print('Lmao') #best error message ever