
import os
import subprocess
from skillbridge import Workspace
import skillbridge


#load("/home/jehess/miniforge3/envs/morpheus/lib/python3.11/site-packages/skillbridge/server/python_server.il")
#cadence = subprocess.Popen(["virtuoso", "-nograph"],stdin=subprocess.PIPE,stdout=PIPE, stderr=PIPE)
#cadence.stdin.write(b"load('/home/jehess/miniforge3/envs/morpheus/lib/python3.11/site-packages/skillbridge/server/python_server.il')")


#start cadence
cadence = subprocess.Popen(["virtuoso", "-nograph"],stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#get skillbridge module path
file_path = skillbridge.__file__
dir = os.path.dirname(file_path)
command = dir + "server/python_server.il" #server location
#/home/jehess/miniforge3/envs/morpheus/  lib/python3.11/site-packages/skillbridge/server/python_server.il
#/home/jehess/miniforge3/envs/morpheus/bin/python/lib/python3.11/site-packages/skillbridge/server/python_server.il"
#cadence.stdin.write(b"load('/home/jehess/miniforge3/envs/morpheus/lib/python3.11/site-packages/skillbridge/server/python_server.il')")
