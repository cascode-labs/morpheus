
from skillbridge import Workspace
import sys
import os.path
from morpheus.Maestro import maestro
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.Schematic import schematic
from morpheus import Config
from morpheus import *

id = "test"
lib = "morpheus_tests"
DUT = "iopamp"
configFile = "Schematics/opamp.yml"
tconfig = None

ws = Workspace.open(id)

DUT = ws.db.open_cell_view("morpheus_tests","opamp","symbol")
configFile = Config.config(configFile)
Testbench = maestro(ws,lib,DUT,test = configFile)
