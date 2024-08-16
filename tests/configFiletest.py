
from skillbridge import Workspace
import sys
import os.path
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.Maestro import maestro
from morpheus.Schematic import schematic
from morpheus import Config
from morpheus.Config import config, config_types
from morpheus import *

id = "test"
lib = "morpheus_tests"
DUT = "5T_Op_Amp"
configFile = "opamp"
tconfig = None

config.getPaths() #TODO call this in CONFIG NOT IN MORPHEUS main

#Get all Tests 
files = config.searchFiles(file_type=config_types.TEST)
configs = list()

for file in files:
    print(file)
    new_config = config(filepath=file)

#get specific filepath

#get name with type


