import morpheus

from skillbridge import Workspace

from morpheus import Schematic

id = "test"
lib = "morpheus"
DUT = "iopamp"
config = "opamp.yml"
tconfig = None

ws = Workspace.open(id)

Testbench = Schematic.schematic(ws,lib,DUT,config, tconfig)
