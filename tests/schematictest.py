import sys
import os.path
#print(os.getcwd())
#parentddir = os.path.abspath(os.path.pardir)
#print(parentddir) #get the parent directory (where morpheus is)
sys.path.append(os.getcwd())
print(sys.path)
from skillbridge import Workspace
from morpheus import *
from morpheus.Schematic import *
from morpheus.Config import  *


id = "test"
ws = Workspace.open(id)



lib = "morpheus_tests"
cell = "opamp_openloop_example"
Global_Dict = {
    "DUTLIB":"morpheus_tests",
    "DUTCELL":"opamp"
    }
configFile = "opamp"
schematic_config = config(configFile,Config.config_types.SCHEMATIC)

#try:
Testbench = schematic(ws, schematic_config, lib, cell, Global_Dict)
Testbench.evaluate();
Testbench.plan();
Testbench.build();

#except FileNotFoundError:
 #   print("FILE NOT FOUND, SCHEMATIC NOT CREATED!")
