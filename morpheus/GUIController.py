from morpheus.Exceptions.ExceptionHandler import MorpheusExceptionHandler

from skillbridge import Workspace
from morpheus.Config import config, config_types
from morpheus.Maestro import maestro
from morpheus.GUIViewer import *
from morpheus.TabTemplate import TabTemplate
import wx
import os

class GUIController():
    MorpheusExceptionHandler()
    def __init__(self, id) -> None:
        self.MEH =  MorpheusExceptionHandler()

        self.MorpheusApp = wx.App()
        self.GUIframe = GUIViewer(None,wx.ID_ANY, "")
        self.id = id
        self.libList = None
        self.cellList = None    

        self.testPins = []
        self.schems = []
        #print("id is ", self.id)
        self.ws = Workspace.open(self.id) #open skillbridge
        #try:
        #    print("create ws")
       #     self.ws = Workspace.open(self.id) #open skillbridge
        #except Exception as e:
        #    print("failed to create ws")
        #    self.error(e)


    def startGUI(self):

        '''Start GUI Mainloop and initiate Bindings'''

        self.MorpheusApp.SetTopWindow(self.GUIframe) # Initilize GUI
        self.GUIframe.Size = (600,265)
        self.GUIframe.Show()

        self.setBindings() # Initiate Bindings
        self.populateLibraries() # Populate Library drop down menu
        self.populateTests()

        self.MorpheusApp.MainLoop() # Start Main Loop

    
    def setBindings(self):

        '''Function to handle the bindings of every element on the GUI'''

        self.GUIframe.sel_dut_lib.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.populateCells)
        self.GUIframe.btn_reeval.Bind(wx.EVT_BUTTON, self.reevaluate)
        self.GUIframe.btn_mktest.Bind(wx.EVT_BUTTON, self.createTest)
        
        ### If more buttons are added, their bindings should be added here unless in notebook pane

    def populateTests(self):
        
        #Files = os.listdir('Test_bench_definitions/Tests') #TODO add check for user directories
        Files = config.getConfigs(config_types.TEST)
        tests = list()
        for file in Files:
            tests.append(file.name)
        
        
        #for test in Files:
        #    tests.append(test[0:(len(test)-4)])

        self.GUIframe.sel_test.AppendItems(tests)

    def populateLibraries(self):

        '''Function used to populate library drop down'''

        self.libList = [lib.name for lib in self.ws.dd.GetLibList()] #Get list of available libraries

        self.GUIframe.sel_lib.AppendItems(self.libList) #Append to drop downs
        self.GUIframe.sel_dut_lib.AppendItems(self.libList) 

    
    def populateCells(self,e):

        '''Function used to poupulate the Cells within a given library'''

        sel = self.GUIframe.sel_dut_lib.GetSelection() #Gets current combo box selection

        if sel != -1:  # Makes sure combo box is not empty

            selectedLib = self.libList[self.GUIframe.sel_dut_lib.GetSelection()] #Gets library from given selection index

            lID = self.ws.dd.GetObj(selectedLib)
            if not lID.cells is None:
                self.cellList = [cell.name for cell in lID.cells] #Populates a list of available cell views
                self.GUIframe.sel_dut_cell.SetItems(self.cellList) #Updates combo box drop down menu
                
    
    def createTest(self,e):

        '''Create a new Test and Maestro View'''

        self.maestro = maestro.createMaestroView(self.ws,self.libList[self.GUIframe.sel_dut_lib.GetSelection()],
                                  self.cellList[self.GUIframe.sel_dut_cell.GetSelection()],
                                  self.libList[self.GUIframe.sel_lib.GetSelection()])

        test = config("Tests/"+ self.GUIframe.sel_test.GetValue() + ".yml") #Load test config YAML
        
        schem = self.maestro.getSchematic(test)  #Create test schematic cooresponding to YAML
        self.maestro.createConfig(test)
        self.maestro.createTest(test,schem)            #Create test in Maestro view cooresponding to YAML

    
        evaluatedPins = schem.evaluatedPins
        self.GUIframe.testbench_tabs.Show() #Unhide Notebook view
        self.GUIframe.btn_reeval.Show()

        generate_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
        self.GUIframe.testbench_tabs.AddPage(generate_tab, self.GUIframe.sel_test.GetValue())

        device_sel_grid = wx.FlexGridSizer(len(schem.evaluatedPins), 2, 0, 0) #Configure Notebook tab
        device_sel_grid.AddGrowableCol(1)
        self.GUIframe.Size = (600,800)

        types = [pin.type for pin in schem.config.Terminals]       #Gather pin types for comboboxes 

        self.schems.append(schem)                  #Append new schematic to list
        self.testPins.append(evaluatedPins)        #Append evaluated pins to list

        for pin in evaluatedPins:
            pinLabel = wx.StaticText(generate_tab,wx.ID_ANY, pin.label)           #Create Pin Label
            device_sel_grid.Add(pinLabel, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 0) 

            pinSelect = wx.ComboBox(generate_tab, wx.ID_ANY,name=pin.label, choices=types, style=wx.CB_DROPDOWN | wx.CB_READONLY)#Create Pin type select box
            if pin.type:
                pinSelect.SetSelection(pinSelect.FindString(pin.type)) #Set Default combobox value to predetermined pin type, or leave blank
            device_sel_grid.Add(pinSelect, 0, wx.ALL | wx.EXPAND, 2)

            pinSelect.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.updateTerminal) #Set Combobox binding for updating pins

    
        generate_tab.sizer_2.Add(device_sel_grid, 0, wx.EXPAND, 0)
        generate_tab.SetSizer(generate_tab.sizer_2)
        generate_tab.Layout()
 
    def updateTerminal(self,e):

        '''Function used to update Terminal model when Pin selection is changed'''

        ComboBox = e.GetEventObject() #Get which Combobox triggered the event
        PinLabel = ComboBox.GetName() #Get the name of the combobox representing the pin

        EvalPins = self.testPins[self.GUIframe.testbench_tabs.GetSelection()] #Grab pin list based on tab
        schem = self.schems[self.GUIframe.testbench_tabs.GetSelection()] #Grab schematic based on tab

        pin_types = {schem.config.Terminals[i].type: schem.config.Terminals[i] 
                     for i in range(len(schem.config.Terminals))} #Gather pin types from schematic


        for pin in EvalPins:
            if pin.label == PinLabel: #Update the given pin with user selected combobox info
                pin.type = ComboBox.GetValue()
                pin_conf = schem.getTerminal(pin_types[pin.type])
                pin.region = pin_types[pin.type].region
                pin.update(pin,pin_conf)

    #TODO Modify so the bulk of the "re-evaluation" function takes place within the Schematic file
    def reevaluate(self,e):

        '''Reevaulate function to rebuild test schematic from user input'''

        cs = self.GUIframe.testbench_tabs.GetSelection()
        schem = self.schems[cs]
        schem.reevaluate(self.testPins[cs])



   # def statusPrint(self, msg):
   #     self.GUIframe.StatusBar.SetStatusText(0,msg);
    

    #TODO error collection function
    def error(self, e):
        #error = self.MEH.catch(e)
        #self.GUI.raiseError(error)
        pass