from .calc_damage import calc_damage
from .help import help_function
from .start import start

def get_commands():
  return [ ( 'help', help_function ), ( 'start', start ) ]

def get_conversations():
  return [ calc_damage ]