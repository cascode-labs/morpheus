#import morpheus

import asyncio
from skillbridge import Workspace
import sys
import os.path
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.Schematic import schematic
from morpheus import Config
#sys.path.append(S
#    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from morpheus import *

id = "test"
lib = "morpheus_tests"
DUT = "iopamp"
configFile = "opamp.yml"
tconfig = None


import subprocess
from subprocess import Popen, PIPE

ws = Workspace.open(id)

DUT = ws.db.open_cell_view("morpheus_tests","opamp","symbol")
configFile = Config.config(configFile,Config.config_types.SCHEMATIC)
Testbench = schematic(ws,lib,DUT,configFile, tconfig)
Testbench.evaluate();
Testbench.plan();
Testbench.build();
# morpheus schematic op