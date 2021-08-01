from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

help_message = """List of available commands:
- /calc_damage, to calculate the damage given a Defender and an Attacker Pokémon and a Move (you can also customize the field and other options too)
- /help, to show the full list of commands and the credits

This bot was made by Simone Alghisi, as an experiment to learn something out of Python. If you want to report a bug or something doesn't feels right, please open a pull request on GitHub (https://github.com/Simone-Alghisi/Pkmn-dmg-calc-bot/issues/new).

If you want to check out the Python code you can find it here: https://github.com/Simone-Alghisi/Pkmn-dmg-calc-bot.

The bot uses the code available from Smogon to calculate the damage (if you are interested you can find it here: https://github.com/smogon/damage-calc)."""  

def help_function(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(help_message)