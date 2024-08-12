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
configFile = "opamp"
tconfig = None



