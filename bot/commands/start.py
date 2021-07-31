from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

start_message = """Hi {}, this is a bot to calculate the damage output given a Defender and an Attacker Pokémon and a Move (you can also customize the field and other options too).
Please use /help for a full list of commands.

Credits obviously to Smogon for the damage calculator implementation.
If you receive some kind of error you can contact @Alghisius and hope that he'll fix that soon... maybe"""  

def start(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(start_message.format(update.effective_user.first_name))