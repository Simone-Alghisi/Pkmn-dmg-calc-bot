from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext, MessageHandler, Filters
import logging
import pandas as pd
import math
import json
import subprocess
import os

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH, SEVENTH, EIGTH, NINTH, TENTH, ELEVENTH, TWELFTH, THIRTEENTH, FOURTEENTH, FIFTEENTH, SIXTEENTH, SEVENTEENTH, EIGHTEENTH, LAST = range(19)
# Read DataFrame Pkmns
PKMN_DATASET = pd.read_csv("config/pokedex.csv")
# EVs Dict
EVs = {"HP": "Atk", "Atk": "Def", "Def": "SpA", "SpA": "SpD", "SpD": "Spe", "Spe": 1, 1: "HP"} #Cyclic to prevent some kind of error
# Read DataFrame Natures
NATURES_DATASET = pd.read_csv("config/natures.csv").values.tolist()
# Read DataFrame Items
ITEMS_DATASET = pd.read_csv("config/items.csv")
# Read DataFrame Moves
MOVES_DATASET = pd.read_csv("config/moves.csv")
# Field Attributes
TERRAIN, WEATHER, GRAVITY, ROCKS, STEELSURGE, VINELASH, WILDFIRE, CANNONADE, VOLCALITH, SPIKES, REFLECT, LIGHTSCREEN, PROTECT, SEEDS, HELPINGHAND, FRIENDGUARD, AURORAVEIL, BATTERY, SWITCH, CRIT, DYNA_ATT, DYNA_DEF, BURN_ATT, BURN_DEF, POISON, BAD_POISON, ATK, SPA, DEF, SPD, OTHERS = range(2, 33)
# Terrain Dict
TERRAINS_DICT = {'None': 'Electric', 'Electric': 'Grassy', 'Grassy': 'Misty', 'Misty': 'Psychic', 'Psychic': 'None'}
# Weather Dict
WEATHER_DICT = {'None': 'Sun', 'Sun': 'Rain', 'Rain': 'Sand', 'Sand': 'Hail', 'Hail': 'Harsh Sunshine', 'Harsh Sunshine': 'Heavy Rain', 'Heavy Rain': 'Strong Winds', 'Strong Winds': 'None'}
# Boost Dict
BOOST_DICT = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: -1, -1: -2, -2: -3, -3: -4, -4: -5, -5: -6, -6: 0}
# Error Message
# TODO... change this to your discretion
ERROR_MSG = "An unexpected error occurred and the conversation ended: please try again.\nIf the problem persists, notify to @Alghisius"

def calc_damage():
  return ConversationHandler(
    entry_points=[CommandHandler('calc_damage', start)],
      states={
        FIRST: [
          CallbackQueryHandler(retrieve_pkmn, pattern='^[A-Z]{1}$'),
          CallbackQueryHandler(end, pattern='^0$')
        ],
        SECOND: [
          CallbackQueryHandler(previous_element, pattern='^-1$'),
          CallbackQueryHandler(back, pattern='^0$'),
          CallbackQueryHandler(next_element, pattern='^1$'),
          CallbackQueryHandler(pick_pkmn, pattern='^[-a-zA-Z0-9%_ ]+$')
        ],
        THIRD: [
          CallbackQueryHandler(set_stats, pattern='^[0-9]+$'),
          CallbackQueryHandler(back_to_list, pattern='^-1$'),
          CallbackQueryHandler(pick_nature, pattern='^-2$')
        ],
        FOURTH: [
          CallbackQueryHandler(back_to_stats, pattern='^0$'),
          CallbackQueryHandler(set_nature, pattern='^[a-zA-Z]+$')
        ],
        FIFTH: [
          CallbackQueryHandler(retrieve_item, pattern='^[A-Z]{1}$'),
          CallbackQueryHandler(pick_nature, pattern='^0$'),
          CallbackQueryHandler(pick_item, pattern='^1$')
        ],
        SIXTH: [
          CallbackQueryHandler(previous_item, pattern='^-1$'),
          CallbackQueryHandler(back_to_items, pattern='^0$'),
          CallbackQueryHandler(next_item, pattern='^1$'),
          CallbackQueryHandler(pick_item)
        ],
        SEVENTH: [
          CallbackQueryHandler(retrieve_ability, pattern='^-1$'),
          CallbackQueryHandler(back_to_items_list, pattern='^0$'),
          CallbackQueryHandler(choose_opponent, pattern='^1$')
        ],
        EIGTH: [
          CallbackQueryHandler(pick_item, pattern='^0$'),
          CallbackQueryHandler(choose_opponent)
        ],
        NINTH: [
          CallbackQueryHandler(pick_item, pattern='^0$'),
          CallbackQueryHandler(retrieve_opponent, pattern='^[A-Z]{1}$')
        ],
        TENTH: [
          CallbackQueryHandler(previous_opponent, pattern='^-1$'),
          CallbackQueryHandler(choose_opponent, pattern='^0$'),
          CallbackQueryHandler(next_opponent, pattern='^1$'),
          CallbackQueryHandler(pick_opponent, pattern='^[-a-zA-Z0-9%_ ]+$')
        ],
        ELEVENTH: [
          CallbackQueryHandler(set_opponent_stats, pattern='^[0-9]+$'),
          CallbackQueryHandler(back_to_opponents, pattern='^-1$'),
          CallbackQueryHandler(pick_opponent_nature, pattern='^-2$')
        ],
        TWELFTH: [
          CallbackQueryHandler(back_to_opponent_stats, pattern='^0$'),
          CallbackQueryHandler(set_opponent_nature, pattern='^[a-zA-Z]+$'),
        ],
        THIRTEENTH: [
          CallbackQueryHandler(retrieve_opponent_item, pattern='^[A-Z]{1}$'),
          CallbackQueryHandler(pick_opponent_nature, pattern='^0$'),
          CallbackQueryHandler(pick_opponent_item, pattern='^1$')
        ],
        FOURTEENTH: [
          CallbackQueryHandler(previous_opponent_item, pattern='^-1$'),
          CallbackQueryHandler(back_to_opponent_items, pattern='^0$'),
          CallbackQueryHandler(next_opponent_item, pattern='^1$'),
          CallbackQueryHandler(pick_opponent_item)
        ],
        FIFTEENTH: [
          CallbackQueryHandler(retrieve_opponent_ability, pattern='^-1$'),
          CallbackQueryHandler(back_to_opponent_items_list, pattern='^0$'),
          CallbackQueryHandler(choose_move, pattern='^1$')
        ],
        SIXTEENTH: [
          CallbackQueryHandler(pick_opponent_item, pattern='^0$'),
          CallbackQueryHandler(choose_move)
        ],
        SEVENTEENTH: [
          CallbackQueryHandler(pick_opponent_item, pattern='^0$'),
          CallbackQueryHandler(retrieve_move, pattern='^[A-Z]{1}$')
        ],
        EIGHTEENTH: [
          CallbackQueryHandler(previous_move, pattern='^-1$'),
          CallbackQueryHandler(back_to_moves, pattern='^0$'),
          CallbackQueryHandler(next_move, pattern='^1$'),
          CallbackQueryHandler(pick_move)
        ],
        LAST: [
          CallbackQueryHandler(calculate, pattern='^1$'),
          CallbackQueryHandler(back_to_moves_list, pattern='^0$'),
           CallbackQueryHandler(end, pattern='^-2$'),
          CallbackQueryHandler(change_settings)
        ],
        ConversationHandler.TIMEOUT: [
          MessageHandler(Filters.text|Filters.command, timeout_exceeded)
        ]
      },
      # fallbacks are used when there's no match in a particular state
      fallbacks=[CallbackQueryHandler(wrong_state)],
      conversation_timeout=60*15
  )

def print_pkmn(pkmn) -> str:
  if pkmn is not None:
    text_to_return = ""
    if 'name' in pkmn:
      text_to_return = "".join((text_to_return, pkmn['name']))
    if 'item' in pkmn:
      text_to_return = "".join((text_to_return, f" @ {pkmn['item']}"))
    if 'ability' in pkmn:
      text_to_return = "".join((text_to_return, f"\nAbility: {pkmn['ability']}"))
    if 'evs' in pkmn:
      text_to_return = "".join((text_to_return, f"\nEVs: {pkmn['HP']} HP / {pkmn['Atk']} Atk / {pkmn['Def']} Def / {pkmn['SpA']} SpA / {pkmn['SpD']} SpD / {pkmn['Spe']} Spe"))
    if 'nature' in pkmn:
      text_to_return = "".join((text_to_return, f"\n{pkmn['nature']} Nature"))
    return text_to_return
  else:
    return "Could not print this Pokémon information\n"

def start(update, context):
  user = update.message.from_user
  context.user_data['user_id'] = user.id
  logger.info(f"User {user.first_name} ({user.id}) started the conversation.")
  reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard())
  update.message.reply_text("Choose the starting letter of the Defending Pokémon", reply_markup=reply_markup)
  return FIRST

def generate_alphabetical_keyboard(addNone=False):
  keyboard = [ [InlineKeyboardButton(chr(letter), callback_data=chr(letter)) for letter in range(letter, letter+5) if letter < 91] for letter in range(65, 91, 5) ]
  if addNone:
    keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0), InlineKeyboardButton(text="None", callback_data=1)])
  else:
    keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
  return keyboard

def timeout_exceeded(update, context):
  logger.info("The conversation exceeded the time limit")
  update.message.reply_text("The conversation exceeded the time limit: please use the command /take_damage to start a new conversation")
  return ConversationHandler.END

def end(update, context):
  query = update.callback_query
  query.answer()
  query.edit_message_text(text="The conversation ended: hope to see you soon")
  return ConversationHandler.END

def wrong_state(update, context):
  query = update.callback_query
  query.answer()
  logger.error("The user ended up a in state which is not handled in any way")
  query.edit_message_text(text=ERROR_MSG)
  return ConversationHandler.END

def generate_list(retrieve, obj_index, choices_to_display):
  keyboard = []
  for index in range(obj_index, obj_index+10, 5):
    row = []
    for i in range(index, index+5):
      if i < len(retrieve):
        row.append(InlineKeyboardButton(i%10, callback_data=retrieve[i]))
        choices_to_display = "".join((choices_to_display, f"{i%10}) {retrieve[i]}\n"))
    keyboard.append(row)
  row = [InlineKeyboardButton(text=u"\u2B05", callback_data=-1), InlineKeyboardButton(text=u"\u274C", callback_data=0), InlineKeyboardButton(text=u"\u27A1", callback_data=1)]
  keyboard.append(row)
  return keyboard, choices_to_display

def retrieve_pkmn(update, context):
  query = update.callback_query
  choice = str(query.data)
  query.answer()
  if choice is not None:
    retrieve = PKMN_DATASET[PKMN_DATASET['name'].str.startswith(choice)]
    pkmn_index = 0
    retrieve = retrieve['name'].tolist()
    context.user_data['retrieve'] = retrieve
    context.user_data['index'] = pkmn_index
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, pkmn_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return SECOND
  else:
    logger.error("Choice is None in retrieve_pkmn: no letter selected from the keyboard")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def previous_element(update, context):
  query = update.callback_query
  if 'retrieve' in context.user_data and 'index' in context.user_data:
    retrieve = context.user_data['retrieve']
    pkmn_index = context.user_data['index']
    if pkmn_index-10 >= 0:
      query.answer()
      pkmn_index -= 10
      context.user_data['index'] = pkmn_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, pkmn_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No previous information to display')
    return SECOND
  else:
    query.answer()
    if not 'retrieve' in context.user_data:
      logger.error("To put it simply the list of pokémon exploded for no reason")
    else:
      logger.error("To put it simply the index to the pokémon list exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def next_element(update, context):
  query = update.callback_query
  if 'retrieve' in context.user_data and 'index' in context.user_data:
    retrieve = context.user_data['retrieve']
    pkmn_index = context.user_data['index']
    if pkmn_index+10 < len(retrieve):
      query.answer()
      pkmn_index += 10
      context.user_data['index'] = pkmn_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, pkmn_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No further information to display')
    return SECOND
  else:
    query.answer()
    if not 'retrieve' in context.user_data:
      logger.error("To put it simply the list of pokémon exploded for no reason")
    else:
      logger.error("To put it simply the index to the pokémon list exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END
    
def back(update, context):
  query = update.callback_query
  query.answer()
  reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard())
  query.edit_message_text("Choose the starting letter of the Defending Pokémon", reply_markup=reply_markup)
  return FIRST

def pick_pkmn(update, context):
  query = update.callback_query
  query.answer()
  defender = str(query.data)
  if defender is not None:
    context.user_data['defender'] = {
      'name': defender,
      'evs': 508,
      'HP': 0,
      'Atk': 0,
      'Def': 0,
      'SpA': 0,
      'SpD': 0,
      'Spe': 0
    }
    keyboard = [ [InlineKeyboardButton(text="Set Evs", callback_data=253), InlineKeyboardButton(text=u"\u274C", callback_data=-1), InlineKeyboardButton(text="Skip to Nature", callback_data=-2)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"{defender} will be the Pokémon which will take damage due to a move from the Opponent\nYou can now set its EVs or you skip this part and go set its the Nature", reply_markup=reply_markup
    )
    return THIRD
  else:
    logger.error("Defender is None in pick_pkmn: no pokémon selected from the list")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_list(update, context):
  query = update.callback_query
  query.answer()
  if 'retrieve' in context.user_data and 'index' in context.user_data:
    retrieve = context.user_data['retrieve']
    pkmn_index = context.user_data['index']
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, pkmn_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return SECOND
  else:
    if not 'retrieve' in context.user_data:
      logger.error("To put it simply the list of pokémon exploded for no reason while going 'back'")
    else:
      logger.error("To put it simply the index to the pokémon list exploded for no reason while going 'back'")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def set_stats(update, context):
  query = update.callback_query
  stat_value = int(query.data)
  query.answer()
  if stat_value is not None and 'defender' in context.user_data:
    defender = context.user_data['defender']
    if stat_value == 253:
      context.user_data['current_stat'] = "HP"
    elif stat_value >= 0 and 'current_stat' in context.user_data:
      defender[context.user_data['current_stat']] = stat_value
      defender['evs'] -= stat_value
      context.user_data['current_stat'] = EVs[context.user_data['current_stat']]
    if 'current_stat' in context.user_data and context.user_data['current_stat'] == 1:
      text_to_display = f"Defender: {print_pkmn(defender)}\n\nIf these stats are correct please choose a Nature:\n"
      keyboard = []
      for index in range(0, len(NATURES_DATASET), 5):
        row = []
        for i in range(index, index+5):
          if i < len(NATURES_DATASET):
            row.append(InlineKeyboardButton(i, callback_data=NATURES_DATASET[i][0]))
            to_join = ""
            if NATURES_DATASET[i][1] != NATURES_DATASET[i][1]:
              to_join = f"{i}) {NATURES_DATASET[i][0]}\n"
            else:
              to_join = f"{i}) {NATURES_DATASET[i][0]} (+{NATURES_DATASET[i][1]}, -{NATURES_DATASET[i][2]})\n"
            text_to_display = "".join((text_to_display, to_join))
        keyboard.append(row)
      keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=text_to_display, reply_markup=reply_markup
      )
      return FOURTH
    else:
      # build a keyboard for the next stats
      keyboard = [InlineKeyboardButton(text=0, callback_data=0)]
      if defender['evs'] >= 4:
        keyboard.append(InlineKeyboardButton(text=4, callback_data=4))
      if defender['evs'] >= 12:
        keyboard.append(InlineKeyboardButton(text=12, callback_data=12))
      if defender['evs'] >= 20:
        keyboard.append(InlineKeyboardButton(text=20, callback_data=20))
      keyboard = [ keyboard ]
      keyboard.extend([InlineKeyboardButton(index, callback_data=index) for index in range(i, i+8*3+1, 8) if index <= defender['evs'] and index <= 252] for i in range(28, 253, 32))
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=f"Pick the number of EVs that {defender['name']} should have in {context.user_data['current_stat']}", reply_markup=reply_markup
      )
      return THIRD
  else:
    if not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in set_stats")
    else:
      logger.error("To put it simply the stat_value exploded for no reason in set_stats")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def pick_nature(update, context):
  query = update.callback_query
  query.answer()
  if 'defender' in context.user_data:
    defender = context.user_data['defender']
    text_to_display = f"Defender:\n{print_pkmn(defender)}\n\nIf these stats are correct please choose a Nature:\n"
    keyboard = []
    for index in range(0, len(NATURES_DATASET), 5):
      row = []
      for i in range(index, index+5):
        if i < len(NATURES_DATASET):
          row.append(InlineKeyboardButton(i, callback_data=NATURES_DATASET[i][0]))
          to_join = ""
          if NATURES_DATASET[i][1] != NATURES_DATASET[i][1]:
            to_join = f"{i}) {NATURES_DATASET[i][0]}\n"
          else:
            to_join = f"{i}) {NATURES_DATASET[i][0]} (+{NATURES_DATASET[i][1]}, -{NATURES_DATASET[i][2]})\n"
          text_to_display = "".join((text_to_display, to_join))
      keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
      text=text_to_display, reply_markup=reply_markup
    )
    return FOURTH
  else:
    logger.error("To put it simply the defender pokémon exploded for no reason in pick_nature")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_stats(update, context):
  query = update.callback_query
  query.answer()
  if 'defender' in context.user_data:
    defender = context.user_data['defender']
    defender['evs'] = 508
    defender['HP'] = defender['Atk'] = defender['Def'] = defender['SpA'] = defender['SpD'] = defender['Spe'] = 0
    keyboard = [ [InlineKeyboardButton(text="Set Evs", callback_data=253), InlineKeyboardButton(text=u"\u274C", callback_data=-1), InlineKeyboardButton(text="Skip to Nature", callback_data=-2)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"{defender['name']} will be the Pokémon which will take damage due to a move from the Opponent\nYou can now set its EVs or you skip this part and go set its the Nature", reply_markup=reply_markup
    )
    return THIRD
  else:
    logger.error("To put it simply the defender pokémon exploded for no reason in back_to_stats")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def set_nature(update, context):
  query = update.callback_query
  nature = str(query.data)
  query.answer()
  if nature is not None and 'defender' in context.user_data:
    defender = context.user_data['defender']
    defender['nature'] = nature
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard(True))
    query.edit_message_text(f"Defender:\n{print_pkmn(defender)}\n\nChoose the Item that {defender['name']} will hold\nPick None if you want to skip to the next part", reply_markup=reply_markup)
    return FIFTH
  else:
    if not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in set_nature")
    else:
      logger.error("To put it simply the nature passed as callback_data exploded for no reason in set_nature")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def retrieve_item(update, context):
  query = update.callback_query
  choice = str(query.data)
  query.answer()
  if choice is not None:
    retrieve = ITEMS_DATASET[ITEMS_DATASET['name'].str.startswith(choice)]
    retrieve = retrieve['name'].tolist()
    item_index = 0
    context.user_data['retrieve_item'] = retrieve
    context.user_data['item_index'] = item_index
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, item_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return SIXTH
  else:
    logger.error("Choice is None in retrieve_item: no letter selected from the keyboard")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def pick_item(update, context):
  query = update.callback_query
  item = str(query.data)
  query.answer()
  if item is not None and 'defender' in context.user_data:
    defender = context.user_data['defender']
    if item == "1" and 'item' in defender:
      del defender['item']
    if item != "1" and item != "0":
      defender['item'] = item
    recap_text = f"Defender:\n{print_pkmn(defender)}\n\nIf everything it's all right you can now choose {defender['name']}'s ability or you can skip that part and pick the Attacker (Opponent):\n"
    keyboard = [ [InlineKeyboardButton(text="Choose Ability", callback_data=-1), InlineKeyboardButton(text=u"\u274C", callback_data=0), InlineKeyboardButton(text="Skip to Opponent", callback_data=1)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text=recap_text, reply_markup=reply_markup
    )
    return SEVENTH
  else:
    if not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in pick_item")
    else:
      logger.error("To put it simply the item passed as callback_data exploded for no reason in pick_item")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def previous_item(update, context):
  query = update.callback_query
  if 'retrieve_item' in context.user_data and 'item_index' in context.user_data:
    retrieve = context.user_data['retrieve_item']
    item_index = context.user_data['item_index']
    if item_index-10 >= 0:
      query.answer()
      item_index -= 10
      context.user_data['item_index'] = item_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, item_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No previous information to display')
    return SIXTH
  else:
    query.answer()
    if not 'retrieve_item' in context.user_data:
      logger.error("To put it simply the list of item exploded for no reason")
    else:
      logger.error("To put it simply the index to the item list exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def next_item(update, context):
  query = update.callback_query
  if 'retrieve_item' in context.user_data and 'item_index' in context.user_data:
    retrieve = context.user_data['retrieve_item']
    item_index = context.user_data['item_index']
    if item_index+10 < len(retrieve):
      query.answer()
      item_index += 10
      context.user_data['item_index'] = item_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, item_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No further information to display')
    return SIXTH
  else:
    query.answer()
    if not 'retrieve_item' in context.user_data:
      logger.error("To put it simply the list of item exploded for no reason")
    else:
      logger.error("To put it simply the index to the item list exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_items(update, context):
  query = update.callback_query
  query.answer()
  if 'defender' in context.user_data:
    defender = context.user_data['defender']
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard(True))
    query.edit_message_text(f"Defender:\n{print_pkmn(defender)}\n\nChoose the Item that {defender['name']} will hold\nPick None if you want to skip to the next part", reply_markup=reply_markup)
    return FIFTH
  else:
    logger.error("To put it simply the defender pokémon exploded for no reason in back_to_items")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def retrieve_ability(update, context):
  query = update.callback_query
  query.answer()
  if 'defender' in context.user_data and 'name' in context.user_data['defender']:
    defender = context.user_data['defender']
    retrieve = PKMN_DATASET[ PKMN_DATASET['name'] == defender['name'] ]
    ability_1 = retrieve['ability_1'].values[0]
    ability_2 = retrieve['ability_2'].values[0]
    ability_hidden = retrieve['ability_hidden'].values[0]
    text_to_show = f"Select {defender['name']}'s Ability from one of the following..."
    first_row = []
    if ability_1 == ability_1:
      first_row.append(InlineKeyboardButton(text=ability_1, callback_data=ability_1))
    if ability_2 == ability_2:
      first_row.append(InlineKeyboardButton(text=ability_2, callback_data=ability_2))
    keyboard = [first_row]
    if ability_hidden == ability_hidden:
      keyboard.append([InlineKeyboardButton(text=ability_hidden, callback_data=ability_hidden)])
    keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=text_to_show, reply_markup=reply_markup
    )
    return EIGTH
  else:
    if not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in retrieve_ability")
    else:
      logger.error("To put it simply the defender pokémon name exploded for no reason in retrieve_ability")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_items_list(update, context):
  query = update.callback_query
  data = context.user_data
  query.answer()
  if data is not None and 'retrieve_item' in data and 'item_index' in data:
    retrieve = data['retrieve_item']
    item_index = data['item_index']
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, item_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return SIXTH
  elif data is not None and (not 'retrieve_item' in data or not 'item_index' in data) and 'defender' in context.user_data:
    defender = data['defender']
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard(True))
    query.edit_message_text(f"Defender:\n{print_pkmn(defender)}\n\nChoose the Item that {defender['name']} will hold\nPick None if you want to skip to the next part", reply_markup=reply_markup)
    return FIFTH
  else:
    logger.error("To put it simply there are too many things to check but we are in back_to_items_list")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def choose_opponent(update, context):
  query = update.callback_query
  ability = str(query.data)
  query.answer()
  if ability is not None and 'defender' in context.user_data:
    defender = context.user_data['defender']
    if ability == "1" and 'ability' in defender:
      del defender['ability']
    if ability != "1" and ability != "0":
      defender['ability'] = ability
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard())
    query.edit_message_text("Choose the starting letter of the Attacking Pokémon", reply_markup=reply_markup)
    return NINTH
  else:
    if not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in choose_opponent")
    else:
      logger.error("To put it simply the ability passed as callback_data exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def retrieve_opponent(update, context):
  query = update.callback_query
  query.answer()
  choice = str(query.data)
  if choice is not None:
    retrieve = PKMN_DATASET[PKMN_DATASET['name'].str.startswith(choice)]
    retrieve = retrieve["name"].tolist()
    opponent_index = 0
    context.user_data['retrieve_opponent'] = retrieve
    context.user_data['opponent_index'] = opponent_index
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, opponent_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return TENTH
  else:
    logger.error("Choice is None in retrieve_opponent: no letter selected from the keyboard")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def previous_opponent(update, context):
  query = update.callback_query
  if 'retrieve_opponent' in context.user_data and 'opponent_index' in context.user_data:
    retrieve = context.user_data['retrieve_opponent']
    opponent_index = context.user_data['opponent_index']
    if opponent_index-10 >= 0:
      query.answer()
      opponent_index -= 10
      context.user_data['opponent_index'] = opponent_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, opponent_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No previous information to display')
    return TENTH
  else:
    query.answer()
    if not 'retrieve_opponent' in context.user_data:
      logger.error("To put it simply the opponents' list exploded for no reason")
    else:
      logger.error("To put it simply the index to the opponents' list exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def next_opponent(update, context):
  query = update.callback_query
  if 'retrieve_opponent' in context.user_data and 'opponent_index' in context.user_data:
    retrieve = context.user_data['retrieve_opponent']
    opponent_index = context.user_data['opponent_index']
    if opponent_index+10 < len(retrieve):
      query.answer()
      opponent_index += 10
      context.user_data['opponent_index'] = opponent_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, opponent_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No previous information to display')
    return TENTH
  else:
    query.answer()
    if not 'retrieve_opponent' in context.user_data:
      logger.error("To put it simply the opponents' list exploded for no reason")
    else:
      logger.error("To put it simply the index to the opponents' list exploded for no reason")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_opponents(update, context):
  query = update.callback_query
  query.answer()
  if 'retrieve_opponent' in context.user_data and 'opponent_index' in context.user_data:
    retrieve = context.user_data['retrieve_opponent']
    opponent_index = context.user_data['opponent_index']
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, opponent_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return TENTH
  else:
    if not 'retrieve_opponent' in context.user_data:
      logger.error("To put it simply the opponent's list exploded for no reason while going 'back_to_opponents'")
    else:
      logger.error("To put it simply the index to the opponent's list exploded for no reason while going 'back_to_opponents'")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def pick_opponent(update, context):
  query = update.callback_query
  attacker = str(query.data)
  query.answer()
  if attacker is not None and 'defender' in context.user_data:
    context.user_data['attacker'] = {
      'name': attacker,
      'evs': 508,
      'HP': 0,
      'Atk': 0,
      'Def': 0,
      'SpA': 0,
      'SpD': 0,
      'Spe': 0
    }
    keyboard = [ [InlineKeyboardButton(text="Set Evs", callback_data=253), InlineKeyboardButton(text=u"\u274C", callback_data=-1), InlineKeyboardButton(text="Skip to Nature", callback_data=-2)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"{attacker} will be the Pokémon dealing damage to {context.user_data['defender']['name']}\nYou can now set the Attacker's EVs or you skip this part and go set its the Nature", reply_markup=reply_markup
    )
    return ELEVENTH
  else:
    if attacker is None:
      logger.error("Attacker is None in pick_pkmn: no pokémon selected from the list")
    else:
      logger.error("To put it simply the defender pokémon exploded for no reason in pick_opponent")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def set_opponent_stats(update, context):
  query = update.callback_query
  stat_value = int(query.data)
  query.answer()
  if stat_value is not None and 'attacker' in context.user_data:
    attacker = context.user_data['attacker']
    if stat_value == 253:
      context.user_data['current_opponent_stat'] = "HP"
    elif stat_value >= 0 and 'current_opponent_stat':
      attacker[context.user_data['current_opponent_stat']] = stat_value
      attacker['evs'] -= stat_value
      context.user_data['current_opponent_stat'] = EVs[context.user_data['current_opponent_stat']]
    if 'current_opponent_stat' in context.user_data and context.user_data['current_opponent_stat'] == 1:
      text_to_display = f"Attacker: {print_pkmn(attacker)}\n\nIf these stats are correct please choose a Nature:\n"
      keyboard = []
      for index in range(0, len(NATURES_DATASET), 5):
        row = []
        for i in range(index, index+5):
          if i < len(NATURES_DATASET):
            row.append(InlineKeyboardButton(i, callback_data=NATURES_DATASET[i][0]))
            to_join = ""
            if NATURES_DATASET[i][1] != NATURES_DATASET[i][1]:
              to_join = f"{i}) {NATURES_DATASET[i][0]}\n"
            else:
              to_join = f"{i}) {NATURES_DATASET[i][0]} (+{NATURES_DATASET[i][1]}, -{NATURES_DATASET[i][2]})\n"
            text_to_display = "".join((text_to_display, to_join))
        keyboard.append(row)
      keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=text_to_display, reply_markup=reply_markup
      )
      return TWELFTH
    else:
      keyboard = [InlineKeyboardButton(text=0, callback_data=0)]
      if attacker['evs'] >= 4:
        keyboard.append(InlineKeyboardButton(text=4, callback_data=4))
      if attacker['evs'] >= 12:
        keyboard.append(InlineKeyboardButton(text=12, callback_data=12))
      if attacker['evs'] >= 20:
        keyboard.append(InlineKeyboardButton(text=20, callback_data=20))
      keyboard = [ keyboard ]
      keyboard.extend([InlineKeyboardButton(index, callback_data=index) for index in range(i, i+8*3+1, 8) if index <= (context.user_data['attacker'])['evs'] and index <= 252] for i in range(28, 253, 32))
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=f"Pick the number of EVs that {attacker['name']} should have in {context.user_data['current_opponent_stat']}", reply_markup=reply_markup
      )
      return ELEVENTH
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in set_opponent_stats")
    else:
      logger.error("To put it simply the stat_value exploded for no reason in set_opponent_stats")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_opponent_stats(update, context):
  query = update.callback_query
  query.answer()
  if 'attacker' in context.user_data and 'defender' in context.user_data:
    attacker = context.user_data['attacker']
    attacker['evs'] = 508
    attacker['HP'] = attacker['Atk'] = attacker['Def'] = attacker['SpA'] = attacker['SpD'] = attacker['Spe'] = 0
    keyboard = [ [InlineKeyboardButton(text="Set Evs", callback_data=253), InlineKeyboardButton(text=u"\u274C", callback_data=-1), InlineKeyboardButton(text="Skip to Nature", callback_data=-2)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"{attacker['name']} will be the Pokémon dealing damage to {context.user_data['defender']['name']}\nYou can now set the Attacker's EVs or you skip this part and go set its the Nature", reply_markup=reply_markup
    )
    return ELEVENTH
  else:
    if not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in back_to_opponent_stats")
    else:
      logger.error("To put it simply the attacker pokémon exploded for no reason in back_to_opponent_stats")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def pick_opponent_nature(update, context):
  query = update.callback_query
  query.answer()
  if 'attacker' in context.user_data:
    attacker = context.user_data['attacker']
    text_to_display = f"Attacker: {print_pkmn(attacker)}\n\nIf these stats are correct please choose a Nature:\n"
    keyboard = []
    for index in range(0, len(NATURES_DATASET), 5):
      row = []
      for i in range(index, index+5):
        if i < len(NATURES_DATASET):
          row.append(InlineKeyboardButton(i, callback_data=NATURES_DATASET[i][0]))
          to_join = ""
          if NATURES_DATASET[i][1] != NATURES_DATASET[i][1]:
            to_join = f"{i}) {NATURES_DATASET[i][0]}\n"
          else:
            to_join = f"{i}) {NATURES_DATASET[i][0]} (+{NATURES_DATASET[i][1]}, -{NATURES_DATASET[i][2]})\n"
          text_to_display = "".join((text_to_display, to_join))
      keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=text_to_display, reply_markup=reply_markup
    )
    return TWELFTH
  else:
    logger.error("To put it simply the attacker pokémon exploded for no reason in pick_opponent_nature")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def set_opponent_nature(update, context):
  query = update.callback_query
  nature = str(query.data)
  query.answer()
  if nature is not None and 'attacker' in context.user_data:
    attacker = context.user_data['attacker']
    attacker['nature'] = nature
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard(True))
    query.edit_message_text(f"Attacker:\n{print_pkmn(attacker)}\n\nChoose the Item that {attacker['name']} will hold\nPick None if you want to skip to the next part", reply_markup=reply_markup)
    return THIRTEENTH
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in set_opponent_nature")
    else:
      logger.error("To put it simply the nature passed as callback_data exploded for no reason in set_opponent_nature")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def retrieve_opponent_item(update, context):
  query = update.callback_query
  choice = str(query.data)
  query.answer()
  if choice is not None:
    retrieve = ITEMS_DATASET[ITEMS_DATASET['name'].str.startswith(choice)]
    retrieve = retrieve['name'].tolist()
    index_opponent_item = 0
    context.user_data['retrieve_opponent_item'] = retrieve
    context.user_data['index_opponent_item'] = index_opponent_item
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, index_opponent_item, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return FOURTEENTH
  else:
    logger.error("Choice is None in retrieve_opponent_item: no letter selected from the keyboard")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def pick_opponent_item(update, context):
  query = update.callback_query
  item = str(query.data)
  query.answer()
  if item is not None and 'attacker' in context.user_data:
    attacker = context.user_data['attacker']
    if item == "1" and 'item' in attacker:
      del attacker['item']
    if item != "1" and item != "0":
      attacker['item'] = item
    recap_text = f"Attacker:\n{print_pkmn(attacker)}\n\nIf everything it's all right you can now choose {attacker['name']}'s ability or you can skip that part and pick the Move:\n"
    keyboard = [ [InlineKeyboardButton(text="Choose Ability", callback_data=-1), InlineKeyboardButton(text=u"\u274C", callback_data=0), InlineKeyboardButton(text="Skip to Move", callback_data=1)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        text=recap_text, reply_markup=reply_markup
    )
    return FIFTEENTH
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in pick_opponent_item")
    else:
      logger.error("To put it simply the item passed as callback_data exploded for no reason in pick_opponent_item")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def previous_opponent_item(update, context):
  query = update.callback_query
  if 'retrieve_opponent_item' in context.user_data and 'index_opponent_item' in context.user_data:
    retrieve = context.user_data['retrieve_opponent_item']
    index_opponent_item = context.user_data['index_opponent_item']
    if index_opponent_item-10 >= 0:
      query.answer()
      index_opponent_item -= 10
      context.user_data['index_opponent_item'] = index_opponent_item
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, index_opponent_item, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No previous information to display')
    return FOURTEENTH
  else:
    query.answer()
    if not 'retrieve_opponent_item' in context.user_data:
      logger.error("To put it simply the list of item exploded for no reason in retrieve_opponent_item")
    else:
      logger.error("To put it simply the index to the item list exploded for no reason in retrieve_opponent_item")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def next_opponent_item(update, context):
  query = update.callback_query
  if 'retrieve_opponent_item' in context.user_data and 'index_opponent_item' in context.user_data:
    retrieve = context.user_data['retrieve_opponent_item']
    index_opponent_item = context.user_data['index_opponent_item']
    if index_opponent_item+10 < len(retrieve):
      query.answer()
      index_opponent_item += 10
      context.user_data['index_opponent_item'] = index_opponent_item
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, index_opponent_item, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No further information to display')
    return FOURTEENTH
  else:
    query.answer()
    if not 'retrieve_opponent_item' in context.user_data:
      logger.error("To put it simply the list of item exploded for no reason in retrieve_opponent_item")
    else:
      logger.error("To put it simply the index to the item list exploded for no reason in retrieve_opponent_item")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_opponent_items(update, context):
  query = update.callback_query
  query.answer()
  if 'attacker' in context.user_data:
    attacker = context.user_data['attacker']
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard(True))
    query.edit_message_text(f"Attacker:\n{print_pkmn(attacker)}\n\nChoose the Item that {attacker['name']} will hold\nPick None if you want to skip to the next part", reply_markup=reply_markup)
    return THIRTEENTH
  else: 
    logger.error("To put it simply the attacker pokémon exploded for no reason in back_to_opponent_items")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def retrieve_opponent_ability(update, context):
  query = update.callback_query
  query.answer()
  if 'attacker' in context.user_data and 'name' in context.user_data['attacker']:
    attacker = context.user_data['attacker']
    retrieve = PKMN_DATASET[ PKMN_DATASET['name'] == attacker['name'] ]
    ability_1 = retrieve['ability_1'].values[0]
    ability_2 = retrieve['ability_2'].values[0]
    ability_hidden = retrieve['ability_hidden'].values[0]
    text_to_show = f"Select {attacker['name']}'s Ability from one of the following..."
    first_row = []
    if ability_1 == ability_1:
      first_row.append(InlineKeyboardButton(text=ability_1, callback_data=ability_1))
    if ability_2 == ability_2:
      first_row.append(InlineKeyboardButton(text=ability_2, callback_data=ability_2))
    keyboard = [first_row]
    if ability_hidden == ability_hidden:
      keyboard.append([InlineKeyboardButton(text=ability_hidden, callback_data=ability_hidden)])
    keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=text_to_show, reply_markup=reply_markup
    )
    return SIXTEENTH
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in retrieve_opponent_ability")
    else:
      logger.error("To put it simply the attacker pokémon name exploded for no reason in retrieve_opponent_ability")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_opponent_items_list(update, context):
  query = update.callback_query
  data = context.user_data
  query.answer()
  if data is not None and 'retrieve_opponent_item' in data and 'index_opponent_item' in data:
    retrieve = data['retrieve_opponent_item']
    index_opponent_item = data['index_opponent_item']
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, index_opponent_item, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return FOURTEENTH
  elif data is not None and (not 'retrieve_opponent_item' in data or not 'index_opponent_item' in data) and 'attacker' in context.user_data:
    attacker = context.user_data['attacker']
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard(True))
    query.edit_message_text(f"Attacker:\n{print_pkmn(attacker)}\n\nChoose the Item that {attacker['name']} will hold\nPick None if you want to skip to the next part", reply_markup=reply_markup)
    return THIRTEENTH
  else:
    logger.error("To put it simply there are too many things to check but we are in back_to_opponent_items_list")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def choose_move(update, context):
  query = update.callback_query
  ability = str(query.data)
  query.answer()
  if ability is not None and 'attacker' in context.user_data and 'defender' in context.user_data:
    attacker = context.user_data['attacker']
    if ability == "1" and 'ability' in attacker:
      del attacker['ability']
    if ability != "1" and ability != "0":
      attacker['ability'] = ability
    defender_text = print_pkmn(context.user_data['defender'])
    attacker_text = print_pkmn(context.user_data['attacker'])
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard())
    query.edit_message_text(f"Defender:\n{defender_text}\n\nAttacker:\n{attacker_text}\n\nThose are the stats so far, select now the Move", reply_markup=reply_markup)
    return SEVENTEENTH
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in choose_move")
    elif not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in choose_move")
    else:
      logger.error("To put it simply the ability passed as callback_data exploded for no reason in choose_move")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def retrieve_move(update, context):
  query = update.callback_query
  choice = str(query.data)
  query.answer()
  if choice is not None:
    retrieve = MOVES_DATASET[MOVES_DATASET['name'].str.startswith(choice)]
    retrieve = retrieve['name'].tolist()
    move_index = 0
    context.user_data['retrieve_move'] = retrieve
    context.user_data['move_index'] = move_index
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, move_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return EIGHTEENTH
  else:
    logger.error("Choice is None in retrieve_move: no letter selected from the keyboard")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def previous_move(update, context):
  query = update.callback_query
  if 'retrieve_move' in context.user_data and 'move_index' in context.user_data:
    query.answer()
    retrieve = context.user_data['retrieve_move']
    move_index = context.user_data['move_index']
    if move_index-10 >= 0:
      move_index -= 10
      context.user_data['move_index'] = move_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, move_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No previous information to display')
    return EIGHTEENTH
  else:
    query.answer()
    if not 'retrieve_move' in context.user_data:
      logger.error("To put it simply the list of moves exploded for no reason in previous_move")
    else:
      logger.error("To put it simply the index to the list of moves exploded for no reason in previous_move")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def next_move(update, context):
  query = update.callback_query
  if 'retrieve_move' in context.user_data and 'move_index' in context.user_data:
    retrieve = context.user_data['retrieve_move']
    move_index = context.user_data['move_index']
    if move_index+10 < len(retrieve):
      query.answer()
      move_index += 10
      context.user_data['move_index'] = move_index
      choices_to_display = "Pick the one you are referring to...\n\n"
      keyboard, choices_to_display = generate_list(retrieve, move_index, choices_to_display)
      reply_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text(
          text=choices_to_display, reply_markup=reply_markup
      )
    else:
      query.answer(text='No further information to display')
    return EIGHTEENTH
  else:
    query.answer()
    if not 'retrieve_move' in context.user_data:
      logger.error("To put it simply the list of moves exploded for no reason in next_move")
    else:
      logger.error("To put it simply the index to the list of moves exploded for no reason in next_move")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_moves(update, context):
  query = update.callback_query
  query.answer()
  if 'attacker' in context.user_data and 'defender' in context.user_data:
    defender_text = print_pkmn(context.user_data['defender'])
    attacker_text = print_pkmn(context.user_data['attacker'])
    reply_markup = InlineKeyboardMarkup(generate_alphabetical_keyboard())
    query.edit_message_text(f"Defender:\n{defender_text}\n\nAttacker:\n{attacker_text}\n\nThose are the stats so far, select now the Move", reply_markup=reply_markup)
    return SEVENTEENTH
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in back_to_moves")
    else:
      logger.error("To put it simply the defender pokémon exploded for no reason in back_to_moves")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def pick_move(update, context):
  query = update.callback_query
  move = str(query.data)
  query.answer()
  if move is not None and 'defender' in context.user_data and 'attacker' in context.user_data:
    defender_text = print_pkmn(context.user_data['defender'])
    attacker_text = print_pkmn(context.user_data['attacker'])
    context.user_data['move'] = {'name': move}
    init_field_crit_dynamax(context.user_data)
    keyboard = init_keyboard(context.user_data)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"Defender:\n{defender_text}\n\nAttacker:\n{attacker_text}\n\nMove:\n{move}\n\nIf everything is ok you can now click 'Calculate' to get the result damage", reply_markup=reply_markup)
    return LAST
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in pick_move")
    elif not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in pick_move")
    else:
      logger.error("To put it simply the move passed as callback_data exploded for no reason in pick_move")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def change_settings(update, context):
  query = update.callback_query
  data = int(query.data)
  query.answer()
  if data is not None and 'defender' in context.user_data and 'attacker' in context.user_data:
    if data == OTHERS:
      context.user_data['page'] = (context.user_data['page'] % 2) + 1
    elif data == TERRAIN:
      context.user_data['field']['terrain'] = TERRAINS_DICT[context.user_data['field']['terrain']]
    elif data == WEATHER:
      context.user_data['field']['weather'] = WEATHER_DICT[context.user_data['field']['weather']]
    elif data == GRAVITY:
      context.user_data['field']['isGravity'] = not context.user_data['field']['isGravity']
    elif data == ROCKS:
      context.user_data['field']['defenderSide']['isSR'] = not context.user_data['field']['defenderSide']['isSR']
    elif data == STEELSURGE:
      context.user_data['field']['defenderSide']['steelsurge'] = not context.user_data['field']['defenderSide']['steelsurge']
    elif data == VINELASH:
      context.user_data['field']['defenderSide']['vinelash'] = not context.user_data['field']['defenderSide']['vinelash']
    elif data == WILDFIRE:
      context.user_data['field']['defenderSide']['wildfire'] = not context.user_data['field']['defenderSide']['wildfire']
    elif data == CANNONADE:
      context.user_data['field']['defenderSide']['cannonade'] = not context.user_data['field']['defenderSide']['cannonade']
    elif data == VOLCALITH:
      context.user_data['field']['defenderSide']['volcalith'] = not context.user_data['field']['defenderSide']['volcalith']
    elif data == SPIKES:
      context.user_data['field']['defenderSide']['spikes'] = (context.user_data['field']['defenderSide']['spikes'] + 1) % 4
    elif data == REFLECT:
      context.user_data['field']['defenderSide']['isReflect'] = not context.user_data['field']['defenderSide']['isReflect']
    elif data == LIGHTSCREEN:
      context.user_data['field']['defenderSide']['isLightScreen'] = not context.user_data['field']['defenderSide']['isLightScreen']
    elif data == PROTECT:
      context.user_data['field']['defenderSide']['isProtected'] = not context.user_data['field']['defenderSide']['isProtected']
    elif data == SEEDS:
      context.user_data['field']['defenderSide']['isSeeded'] = not context.user_data['field']['defenderSide']['isSeeded']
    elif data == HELPINGHAND:
      context.user_data['field']['attackerSide']['isHelpingHand'] = not context.user_data['field']['attackerSide']['isHelpingHand']
    elif data == FRIENDGUARD:
      context.user_data['field']['defenderSide']['isFriendGuard'] = not context.user_data['field']['defenderSide']['isFriendGuard']
    elif data == AURORAVEIL:
      context.user_data['field']['defenderSide']['isAuroraVeil'] = not context.user_data['field']['defenderSide']['isAuroraVeil']
    elif data == BATTERY:
      context.user_data['field']['attackerSide']['isBattery'] = not context.user_data['field']['attackerSide']['isBattery']
    elif data == SWITCH:
      context.user_data['tmp'] = context.user_data['attacker']
      context.user_data['attacker'] = context.user_data['defender']
      context.user_data['defender'] = context.user_data['tmp']
      del context.user_data['tmp']
      init_field_crit_dynamax(context.user_data)
    elif data == CRIT:
      context.user_data['move']['isCrit'] = not context.user_data['move']['isCrit']
    elif data == DYNA_ATT:
      context.user_data['attacker']['isDynamaxed'] = not context.user_data['attacker']['isDynamaxed']
      context.user_data['move']['useMax'] = not context.user_data['move']['useMax']
    elif data == DYNA_DEF:
      context.user_data['defender']['isDynamaxed'] = not context.user_data['defender']['isDynamaxed']
    elif data == BURN_ATT:
      if context.user_data['attacker']['status'] == '':
        context.user_data['attacker']['status'] = 'Burned'
      else:
        context.user_data['attacker']['status'] = ''
    elif data == ATK:
      context.user_data['attacker']['boost']['atk'] = BOOST_DICT[context.user_data['attacker']['boost']['atk']]
    elif data == SPA:
      context.user_data['attacker']['boost']['spa'] = BOOST_DICT[context.user_data['attacker']['boost']['spa']]
    elif data == DEF:
      context.user_data['defender']['boost']['def'] = BOOST_DICT[context.user_data['defender']['boost']['def']]
    elif data == SPD:
      context.user_data['defender']['boost']['spd'] = BOOST_DICT[context.user_data['defender']['boost']['spd']]
    
    defender_text = print_pkmn(context.user_data['defender'])
    attacker_text = print_pkmn(context.user_data['attacker'])
    move = context.user_data['move']['name']
    keyboard = init_keyboard(context.user_data)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"Defender:\n{defender_text}\n\nAttacker:\n{attacker_text}\n\nMove:\n{move}\n\nIf everything is ok you can now click 'Calculate' to get the result damage", reply_markup=reply_markup)
    return LAST
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in change_settings")
    elif not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in change_settings")
    else:
      logger.error("To put it simply the move passed as callback_data exploded for no reason in change_settings")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def calculate(update, context):
  query = update.callback_query
  query.answer()
  if 'defender' in context.user_data and 'attacker' in context.user_data and 'move' in context.user_data and 'field' in context.user_data and 'user_id' in context.user_data:
    defender = context.user_data['defender']
    attacker = context.user_data['attacker']
    move = context.user_data['move']
    field = context.user_data['field']
    file_name = context.user_data['user_id']
    path = f"pending_take_dmg/{file_name}"
    write_request(path, attacker, defender, move, field)
    process = subprocess.Popen([f'npm start {file_name} pending_take_dmg result_take_dmg'], shell=True)
    destination = f"result_take_dmg/{file_name}"
    process.wait()
    text_to_return = ""
    try:
      with open(destination, "r") as file:
        text_to_return = file.read()
      os.remove(destination)
      os.remove(path)
    except:
      text_to_return = "Could not read the file"
    keyboard = [ [InlineKeyboardButton(text=u"\u274C", callback_data=-1)], [InlineKeyboardButton(text="End Conversation", callback_data=-2)] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=text_to_return, reply_markup=reply_markup
    )
    return LAST
  else:
    if not 'attacker' in context.user_data:
      logger.error("To put it simply the attacker pokémon exploded for no reason in calculate")
    elif not 'defender' in context.user_data:
      logger.error("To put it simply the defender pokémon exploded for no reason in calculate")
    elif not 'move' in context.user_data:
      logger.error("To put it simply the move exploded for no reason in calculate")
    elif not 'fiedl' in context.user_data:
      logger.error("To put it simply the field exploded for no reason in calculate")
    else:
      logger.error("To put it simply the user_id exploded for no reason in calculate")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def back_to_moves_list(update, context):
  query = update.callback_query
  query.answer()
  if 'retrieve_move' in context.user_data and 'move_index' in context.user_data:
    retrieve = context.user_data['retrieve_move']
    move_index = context.user_data['move_index']
    choices_to_display = "Pick the one you are referring to...\n\n"
    keyboard, choices_to_display = generate_list(retrieve, move_index, choices_to_display)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=choices_to_display, reply_markup=reply_markup
    )
    return EIGHTEENTH
  else:
    if not 'retrieve_move' in context.user_data:
      logger.error("To put it simply the list of moves exploded for no reason in back_to_moves_list")
    else:
      logger.error("To put it simply the index to the list of moves exploded for no reason in back_to_moves_list")
    query.edit_message_text(text=ERROR_MSG)
    return ConversationHandler.END

def init_keyboard(user_data):
  keyboard = [[InlineKeyboardButton("Calculate", callback_data=1)]]
  keyboard.append([InlineKeyboardButton("Switch Attacker and Defender", callback_data=SWITCH)])
  if user_data is not None and 'page' in user_data:
    page = user_data['page']

    if page == 1:   
      isAttackerDynamaxed = "No"
      if (user_data['attacker'])['isDynamaxed']:
        isAttackerDynamaxed = "Yes"
      isDefenderDynamaxed = "No"
      if user_data['defender']['isDynamaxed']:
        isDefenderDynamaxed = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Dynamax Atk: ", isAttackerDynamaxed)), callback_data=DYNA_ATT), InlineKeyboardButton("".join(("Dynamax Def: ", isDefenderDynamaxed)), callback_data=DYNA_DEF)])
      
      hh = "No"
      if user_data['field']['attackerSide']['isHelpingHand']:
        hh = "Yes"
      crit = "No"
      if user_data['move']['isCrit']:
        crit = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Helping Hand: ", hh)), callback_data=HELPINGHAND), InlineKeyboardButton("".join(("Crit: ", crit)), callback_data=CRIT)])
      
      atk_boost = user_data['attacker']['boost']['atk']
      def_boost = user_data['defender']['boost']['def']
      keyboard.append([InlineKeyboardButton("".join(("Atk Boost: ", str(atk_boost))), callback_data=ATK), InlineKeyboardButton("".join(("Def Boost: ", str(def_boost))), callback_data=DEF)])
      
      spa_boost = user_data['attacker']['boost']['spa']
      spd_boost = user_data['defender']['boost']['spd']
      keyboard.append([InlineKeyboardButton("".join(("SpA Boost: ", str(spa_boost))), callback_data=SPA), InlineKeyboardButton("".join(("SpD Boost: ", str(spd_boost))), callback_data=SPD)])
      
      reflect = "No"
      if user_data['field']['defenderSide']['isReflect']:
        reflect = "Yes"
      light_screen = "No"
      if user_data['field']['defenderSide']['isLightScreen']:
        light_screen = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Reflect: ", reflect)), callback_data=REFLECT), InlineKeyboardButton("".join(("Light Screen: ", light_screen)), callback_data=LIGHTSCREEN)])
      
      veil = "No"
      if user_data['field']['defenderSide']['isAuroraVeil']:
        veil = "Yes"
      protect = "No"
      if user_data['field']['defenderSide']['isProtected']:
        protect = "Yes"
      
      keyboard.append([InlineKeyboardButton("".join(("Aurora Veil: ", veil)), callback_data=AURORAVEIL), InlineKeyboardButton("".join(("Protect: ", protect)), callback_data=PROTECT)])
      weather = user_data['field']['weather']
      keyboard.append([InlineKeyboardButton("".join(("Weather: ", weather)), callback_data=WEATHER)])
   
    elif page == 2:   
      terrain = user_data['field']['terrain'] 
      keyboard.append([InlineKeyboardButton("".join(("Terrain: ", terrain)), callback_data=TERRAIN)])
      
      gravity = "No"
      if user_data['field']['isGravity']:
        gravity = "Yes"
      fg = "No"
      if user_data['field']['defenderSide']['isFriendGuard']:
        fg = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Gravity: ", gravity)), callback_data=GRAVITY), InlineKeyboardButton("".join(("Friend Guard: ", fg)), callback_data=FRIENDGUARD)])
      
      battery = "No"
      if user_data['field']['attackerSide']['isBattery']:
        battery = "Yes"
      ls = "No"
      if user_data['field']['defenderSide']['isSeeded']:
        ls = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Battery: ", battery)), callback_data=BATTERY), InlineKeyboardButton("".join(("Leech Seed: ", ls)), callback_data=SEEDS)])
      
      vine_lash = "No"
      if user_data['field']['defenderSide']['vinelash']:
        vine_lash = "Yes"
      wild_fire = "No"
      if user_data['field']['defenderSide']['wildfire']:
        wild_fire = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Vine Lash: ", vine_lash)), callback_data=VINELASH), InlineKeyboardButton("".join(("Wild Fire: ", wild_fire)), callback_data=WILDFIRE)])
      
      cannonade = "No"
      if user_data['field']['defenderSide']['cannonade']:
        cannonade = "Yes"
      volcalith = "No"
      if user_data['field']['defenderSide']['volcalith']:
        volcalith = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Cannonade: ", cannonade)), callback_data=CANNONADE), InlineKeyboardButton("".join(("Vocalith: ", volcalith)), callback_data=VOLCALITH)])
      
      steel_surge = "No"
      if user_data['field']['defenderSide']['steelsurge']:
        steel_surge = "Yes"
      sr = "No"
      if user_data['field']['defenderSide']['isSR']:
        sr = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Steel Surge: ", steel_surge)), callback_data=STEELSURGE), InlineKeyboardButton("".join(("Stealth Rock: ", sr)), callback_data=ROCKS)])
      
      spikes = user_data['field']['defenderSide']['spikes']
      burned = "No"
      if user_data['attacker']['status'] == 'Burned':
        burned = "Yes"
      keyboard.append([InlineKeyboardButton("".join(("Spikes: ", str(spikes))), callback_data=SPIKES), InlineKeyboardButton("".join(("Burned: ", burned)), callback_data=BURN_ATT)]) 

  keyboard.append([InlineKeyboardButton("Other Options...", callback_data=OTHERS)])
  keyboard.append([InlineKeyboardButton(text=u"\u274C", callback_data=0)])
  return keyboard

def init_field_crit_dynamax(data):
  if data is not None:
    data['page'] = 1

    data['field'] = {'gameType': 'Doubles'}
    field = data['field']
    field['terrain'] = 'None'
    field['weather'] = 'None'
    field['isGravity'] = False

    data['field']['defenderSide'] = {'spikes': 0}
    defender = data['field']['defenderSide']
    defender['steelsurge'] = False
    defender['vinelash'] = False
    defender['wildfire'] = False
    defender['cannonade'] = False
    defender['volcalith'] = False
    defender['isSR'] = False
    defender['isReflect'] = False
    defender['isLightScreen'] = False
    defender['isProtected'] = False
    defender['isSeeded'] = False
    defender['isFriendGuard'] = False
    defender['isAuroraVeil'] = False

    data['field']['attackerSide'] = {'isHelpingHand': False}
    attacker = data['field']['attackerSide']
    attacker['isBattery'] = False

    data['attacker']['isDynamaxed'] = False
    data['attacker']['boost'] = {'atk': 0}
    data['attacker']['boost']['spa'] = 0
    data['attacker']['status'] = ''

    data['defender']['isDynamaxed'] = False
    data['defender']['boost'] = {'def': 0}
    data['defender']['boost']['spd'] = 0

    data['move']['isCrit'] = False
    data['move']['useMax'] = False

def write_request(path, attacker, defender, move, field):
  try:
    with open(path, 'w') as file:
      file.write('{"attacker": { "name": ')
      file.write(f'"{attacker["name"]}",'),
      file.write('"args": { "level": 50, ')
      if 'item' in attacker:
        file.write(f'"item": "{attacker["item"]}",')
      if 'nature' in attacker:
        file.write(f'"nature": "{attacker["nature"]}",')
      if 'ability' in attacker:
        file.write(f'"ability": "{attacker["ability"]}",')  
      file.write('"evs": {')
      file.write(f'"hp": {attacker["HP"]}, "atk": {attacker["Atk"]}, "def": {attacker["Def"]}, "spa": {attacker["SpA"]}, "spd": {attacker["SpD"]}, "spe": {attacker["Spe"]}')
      file.write('}, "isDynamaxed": ')
      if attacker['isDynamaxed']:
        file.write('true, ')
      else:
        file.write('false, ')
      file.write(f'"boosts": {json.dumps(attacker["boost"])}')
      if attacker["status"] == 'Burned':
        file.write(f', "status": {attacker["status"]}')
      file.write('}')
      file.write('}, "defender": {"name": ')
      file.write(f'"{defender["name"]}",')
      file.write('"args": { "level": 50, ')
      if 'item' in defender:
        file.write(f'"item": "{defender["item"]}",')
      if 'nature' in defender:
        file.write(f'"nature": "{defender["nature"]}",')
      if 'ability' in defender:
        file.write(f'"ability": "{defender["ability"]}",')
      file.write('"evs": {')
      file.write(f'"hp": {defender["HP"]}, "atk": {defender["Atk"]}, "def": {defender["Def"]}, "spa": {defender["SpA"]}, "spd": {defender["SpD"]}, "spe": {defender["Spe"]}')
      file.write('}, "isDynamaxed": ')
      if defender['isDynamaxed']:
        file.write('true, ')
      else:
        file.write('false, ')
      file.write(f'"boosts": {json.dumps(defender["boost"])}')
      file.write('}')
      file.write('}, "move": ')
      file.write(f'{json.dumps(move)}, ')
      file.write(f'"field": {json.dumps(field)}')
      file.write('}')
  except:
    logger.error(f"Something went wrong while creating a file in {path}")
