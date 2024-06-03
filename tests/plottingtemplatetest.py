

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
from morpheus.PlottingTemplate import PlottingTemplate


from morpheus.CadenceManager import cadenceManager



id = "test"
lib = "morpheus_tests"
cell = "templatetest2"
view = "maestro"
template = "Template1"

manager = cadenceManager(id) #, cwd = "", precommand="")
ws = Workspace.open(id)


pt = PlottingTemplate(ws,lib,cell,view) #setup template2 as the maestro to edit


cell = "templatetest1" #copy from template1

pt.import_plotting_template(lib,cell,view,template)
template = "Template2" 
pt.export_plotting_template(lib,cell,view,template) #add same template to same cell
#manager.killCadence()py