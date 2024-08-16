#import morpheus

import asyncio
from skillbridge import Workspace
import sys
import os.path
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.Schematic import schematic
from morpheus.CadenceGUI import cadenceGUI
from morpheus import Config
#sys.path.append(S
#    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from morpheus import *

id = "test"

import subprocess
from subprocess import Popen, PIPE

ws = Workspace.open(id)
#ipc_var = ws.ipc.BeginProcess("sleep 10 ; echo hello")
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

gui = cadenceGUI(ws)
print("COMPLETE!")