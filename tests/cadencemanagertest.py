
import os
import sys


parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.CadenceManager import cadenceManager


manager = cadenceManager("test3")
