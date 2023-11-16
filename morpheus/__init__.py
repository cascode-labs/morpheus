"""Cadence Virtuoso Maestro test bench generator"""
__version__ = '0.0.0'
from morpheus import Schematic

import os
from morpheus import Config
print("morpheus init")
script_dir = os.path.dirname(__file__)
user_home = os.path.expanduser('~')
morpheus_home =  os.path.join(user_home,"morpheus")
