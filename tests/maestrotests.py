
from skillbridge import Workspace
import sys
import os.path
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.Maestro import maestro
from morpheus.Schematic import schematic
from morpheus import Config
from morpheus import *

id = "test"
lib = "morpheus_tests"
DUT = "5T_Op_Amp"
configFile = "opamp"
tconfig = None

ws = Workspace.open(id)

DUT = ws.db.open_cell_view("morpheus_tests",DUT,"symbol")
configFile = Config.config(configFile,Config.config_types.TEST)
global_dict = {
    "DUTCELL":"5T_Op_Amp",
    "DUTLIB":"morpheus_tests"
}

Testbench = maestro(ws,configFile,lib,global_dict)
Testbench.build = True
Testbench.open()
Testbench.createTests()
Testbench.close()
#session = maeOpenSetup("morpheus_tests" "opamp_AUTO_TB" "maestro_test") 
#maeCreateTest("firstTest" ?session session ?lib "morpheus_tests" ?cell "opamp_AUTO_TB" ?view "maestro_test")


#session = maeOpenSetup("tests" "TestMaestro" "maestro")
#maeCreateTest("firstTest" ?session session ?lib "tests" ?cell "TestMaestro" ?view "maestro")