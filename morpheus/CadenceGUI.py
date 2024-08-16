#New Cadence sessions are handled and controlled by cadence manager

import os
import subprocess
import sys
import threading
from time import sleep
from skillbridge import Workspace
from skillbridge import Symbol
import skillbridge

import morpheus




class cadenceGUI:
    def __init__(self,ws):
        self.ws= ws
        self.createform()
        self.display()
        self.form = None

    def callback(self):
        print("hello world")
    def callbackRadion(self):
        print("hello world from radio")
    def createform(self):
        self.radioExample = None
        self.radioExample = self.ws.hi.CreateRadioField(name =Symbol('radioExample'), prompt = "Example Selection", choices= ["option1", "option2","Other"], value = "option1")
        self.fields = [[self.radioExample, [0,0],[600,30],200]]

        self.form = self.ws.hi.CreateAppForm(name = Symbol('morpheusform'), formTitle = "Morpheus Test GUI", fields = self.fields)
                
        #self.form.extraFields=
            #list(None 'optionTwo optionTwo
             #       'optionThree optionThree
			#			'optionFour optionFour)


    def display(self):
        self.ws.hi.DisplayForm(self.form)
        self.waitForCallback()
        
    def waitForCallback(self):
        self.ws["waitForCallback"]()
#ipcSkillProcess?
#ipcBeginProcess
#ipcSignalProcess



