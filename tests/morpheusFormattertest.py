
from skillbridge import Workspace
import sys
import os.path
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
#from morpheus.Maestro import maestro
#from morpheus.Schematic import schematic
#from morpheus import Config
from morpheus import *
from morpheus.Formatter import moprheus_Formatter
import _string

formatter = moprheus_Formatter()
varTest = "hello"
print(formatter.format("format_string test{varTest}",varTest = "goodbye"))