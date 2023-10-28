"""Cadence Virtuoso Maestro test bench generator"""
__version__ = '0.0.0'
from morpheus import Schematic

import os
from morpheus import Config
print("morpheus init")
script_dir = os.path.dirname(__file__)
user_home = os.path.expanduser('~')
morpheus_home =  os.path.join(user_home,"morpheus")
#path_locations = list(os.path.join(script_dir, "Test_bench_definitions"), os.path.join(morpheus_home,"testbenches"))
try:
    Config.config(os.path.join(morpheus_home,"user.yml"))
except FileNotFoundError:
    #create new folder?
    pass