from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

start_message = """Hi {}, this is a bot to calculate the damage output given a Defender and an Attacker Pokémon and a Move (you can also customize the field and other options too).
Please use /help for a full list of commands.

Credits obviously to Smogon for the damage calculator implementation.
If you receive some kind of error you can open an issue on Github and hope that the developer will fix that soon... (further details using /help)"""  

def start(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(start_message.format(update.effective_user.first_name))