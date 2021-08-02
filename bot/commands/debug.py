from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

debug_message = """Sorry {}, the bot is currently under manteinance.

Please try again later"""  

def debug(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(debug_message.format(update.effective_user.first_name))