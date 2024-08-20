from morpheus.Exceptions.ExceptionHandler import MorpheusExceptionHandler

from skillbridge import Workspace
from morpheus.Config import config, config_types
from morpheus.Maestro import maestro
from morpheus.Schematic import schematic
from morpheus.GUIViewer import *
from morpheus.TabTemplate import TabTemplate
import wx
import os
from morpheus import Config


class GUIController():
    MorpheusExceptionHandler()
    def __init__(self, ws) -> None:
        self.MEH =  MorpheusExceptionHandler()

        self.MorpheusApp = wx.App()
        self.GUIframe = GUIViewer(None,wx.ID_ANY, "")
        self.libList = None
        self.cellList = None
        self.configs = None

        self.testPins = []
        self.schems = []
        self.ws = ws

            #DEBUGING TEMP
            # __init__(self,ws,config,lib, global_dict = dict()) -> None:
        #self.maestro = maestro(ws,"default_lib")
        #self.schematic_test = schematic(ws,"")


    def startGUI(self):

        '''Start GUI Mainloop and initiate Bindings'''

        self.MorpheusApp.SetTopWindow(self.GUIframe) # Initilize GUI
        self.GUIframe.Size = (600,265)
        self.GUIframe.Show()

        self.setBindings() # Initiate Bindings
        #self.populateLibraries() # Populate Library drop down menu
        self.populateTests()
        self.GUIframe.Size = (600,800)
        config.getPaths()
        self.openNewTab(Config.config.userConfig)
        #self.openNewTab(self.maestro)
        #self.openNewTab(self.schematic_test)
        self.GUIframe.testbench_tabs.Show()


        self.MorpheusApp.MainLoop() # Start Main Loop

    
    def setBindings(self):

        '''Function to handle the bindings of every element on the GUI'''
        #self.GUIframe.lib_sel.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.populateCells)
        #self.GUIframe.btn_reeval.Bind(wx.EVT_BUTTON, self.reevaluate)
        #self.GUIframe.btn_mktest.Bind(wx.EVT_BUTTON, self.createTest)
        #self.GUIframe.sel_test.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.loadTest)
        self.GUIframe.config_sel.Bind(wx.EVT_COMBOBOX,self.loadTest)
        ### If more buttons are added, their bindings should be added here unless in notebook pane
    def loadTest(self,e):
        #create blank maestro view
        
        sel = self.GUIframe.config_sel.GetSelection() #Gets current combo box selection
        
        if sel != -1:  # Makes sure combo box is not empty
            selectectConfig = self.configs[self.GUIframe.config_sel.GetSelection()] #get config file from loaded files (or just load file)
            self.maestro = maestro(self.ws,selectectConfig)
            self.maestro.gui_setup()
            self.openNewTab(self.maestro)

            #new_config = config(filepath=selectedTest)
            #for var in new_config.variables:
            self.addVariables(selectectConfig)
            #CREATE NEW BOXES FOR VARIABLES
            #lID = self.ws.dd.GetObj(selectedLib)
            #if not lID.cells is None:
            #    self.cellList = [cell.name for cell in lID.cells] #Populates a list of available cell views
            #    self.GUIframe.sel_dut_cell.SetItems(self.cellList) #Updates combo box drop down menu

    def openNewTab(self, obj_to_tab):

        tab_name = "test tab"
        new_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
        new_tab.build(obj_to_tab,self.GUIframe.testbench_tabs)

        # self.GUIframe.testbench_tabs.AddPage(new_tab, tab_name)

        # tab_grid = wx.FlexGridSizer(len(obj_to_tab.__dict__), 2, 0, 0) #Configure Notebook tab
        # tab_grid.AddGrowableCol(1)
        # print("adding props")
        # for prop in obj_to_tab.__dict__:
        #     print("prop add")
        #     #text
        #     txt = wx.StaticText(new_tab, wx.ID_ANY, prop)
        #     tab_grid.Add(txt, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 50)
        #     #dropdown
        #     sel = wx.ComboBox(new_tab, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        #     tab_grid.Add(sel, 0, wx.ALL | wx.EXPAND, 2)

        # new_tab.SetSizer(tab_grid)

        # new_tab.Layout()
    
    def addVariables(self,config):
        self.GUIframe.testbench_tabs.Show() #Unhide Notebook view
        variables = config.variables

        device_sel_grid = wx.FlexGridSizer(len(variables), 2, 1, 0) #Configure Notebook tab
        device_sel_grid.AddGrowableCol(1)
        self.GUIframe.Size = (600,800)

        variables_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
        self.GUIframe.testbench_tabs.AddPage(variables_tab, "VARIABLES")
        for var in variables:
            #TODO CHECK TYPE

            pinLabel = wx.StaticText(variables_tab,wx.ID_ANY, "TESTVAR")    #Create Label
            device_sel_grid.Add(pinLabel, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 0) 

            pinSelect = wx.ComboBox(variables_tab, wx.ID_ANY,name="TESTVAR", choices=["test1","test2"], style=wx.CB_DROPDOWN | wx.CB_READONLY)#Create Pin type select box
           # if pin.type:
            #pinSelect.SetSelection(pinSelect.FindString(pin.type)) #Set Default combobox value to predetermined pin type, or leave blank
            device_sel_grid.Add(pinSelect, 0, wx.ALL | wx.EXPAND, 2)
        self.GUIframe.SetSizer(self.body)
            #pinSelect.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.updateTerminal) #Set Combobox binding for updating pins
    def populateTests(self):
        files = config.searchFiles(file_type=config_types.TEST)

        self.configs = list()
        for file in files:
            #print(file)
            new_config = config(filepath=file)
            self.configs.append(new_config)

        #self.GUIframe.sel_test.AppendItems(files)
        #self.GUIframe.sel_test.AppendItems(tests)
        self.GUIframe.config_sel.AppendItems(files)

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

        test = config(self.GUIframe.sel_test.GetValue(),config_types.TEST) #Load test config YAML
        
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