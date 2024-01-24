#New Cadence sessions are handled and controlled by cadence manager

import os
import subprocess
import sys
import threading
from time import sleep
from skillbridge import Workspace
import skillbridge

import morpheus

if getattr(sys, 'frozen', False): #EXE 
    script_dir = os.path.dirname(sys.executable)
elif __file__: #AS PYTHON CODE
    script_dir = os.path.dirname(__file__)




class cadenceManager:
    def __init__(self,id):
        self.timeout= 300 #5 minute timeout
        self.log_file = os.path.join(os.getcwd(), "virtuoso_log.txt")
        self.createNewCadence(id)
        self.checkInactive()
        #self.loop()
        
    def createNewCadence(self, id):
        
        
        # Run virtuoso with input from a string
        virtuoso_process = subprocess.Popen(["virtuoso", "-nograph"],cwd=os.getcwd(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def log_stdout():
            with open(self.log_file, 'w') as log_file:
                while True:
                    line = virtuoso_process.stdout.readline().decode()
                    if not line:
                        break
                    log_file.write(line)
                    #print(line, end='')  # Print to console ADD DEBUGGER CODE

        log_thread = threading.Thread(target=log_stdout)
        log_thread.start()
        
        # Load python_server.il
        dir = os.path.dirname(script_dir)
        command = dir + "/skill/python_server.il"
        load_command = f'load("{command}")\n'
        
        virtuoso_process.stdin.write(load_command.encode())
        
        pyStartServer = f'pyStartServer(?id "{id}")\n'
        virtuoso_process.stdin.write(pyStartServer.encode())

        virtuoso_process.stdin.close()
        

        command = dir + "/skill/killcadence.il"
        
        attempts = 0

        while attempts < 10:
            try:
                self.ws = Workspace.open(id)
                self.ws['load'](command)
                break;
            except:
                sleep(5)
                attempts += 1
        
        if(attempts>=10):
            print("failed to start ws server.")
            return
            


        self.ws['setstatus']()
        print("Cadence has started")
        
    def checkInactive(self):
        self.status = self.ws['checkstatus']()
        self.ws['clearstatus']()
    def setActive(self):
        self.ws['setstatus']()
    def killCadence(self):
        try:
            self.ws['killcadence']()
        except:
            print("server closed");
    def loop(self):
        while(self.status is not None):
            sleep(self.timeout)
            self.checkInactive()
            #add check to morpheus client
        self.killCadence()
            
        
        
'''
#get skillbridge module path
file_path = skillbridge.__file__
dir = os.path.dirname(file_path)
command = dir + "server/python_server.il" #server location
'''