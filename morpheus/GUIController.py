#from morpheus.Exceptions.ExceptionHandler import MorpheusExceptionHandler

from skillbridge import Workspace
from morpheus.Config import config, config_types
from morpheus.Maestro import maestro
from morpheus.Schematic import schematic
from morpheus.GUIViewer import *
from morpheus.TabTemplate import TabTemplate,gui_option
import wx
import os
from morpheus import Config
logger = logging.getLogger("morpheus")

class GUIController():
    #MorpheusExceptionHandler()
    def __init__(self, ws) -> None:
        #self.MEH =  MorpheusExceptionHandler()

        self.MorpheusApp = wx.App()
        logger.info('Start GUI Viewer')
        self.GUIframe = GUIViewer(None,wx.ID_ANY, "")
        logger.info('GUI Viewer Started!')
        self.libList = None
        self.cellList = None
        self.configs = None

        self.lib = None
        self.global_dict = dict()
        self.config = None

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
        self.populateLibraries() # Populate Library drop down menu
        self.populateTests()
        self.GUIframe.Size = (600,800)
        config.getPaths()
        #self.openNewTab(Config.config.userConfig)
        #self.openNewTab(self.maestro)
        #self.openNewTab(self.schematic_test)
        self.GUIframe.testbench_tabs.Show()


        self.MorpheusApp.MainLoop() # Start Main Loop

    
    def setBindings(self):

        '''Function to handle the bindings of every element on the GUI'''
        #self.GUIframe.lib_sel.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.populateCells)
        #self.GUIframe.btn_reeval.Bind(wx.EVT_BUTTON, self.reevaluate)
        self.GUIframe.run_btn.Bind(wx.EVT_BUTTON, self.createTest)
        self.GUIframe.refresh_btn.Bind(wx.EVT_BUTTON, self.refresh_options)
        #self.GUIframe.sel_test.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.loadTest)
        self.GUIframe.config_sel.Bind(wx.EVT_COMBOBOX,self.loadTest)
        self.GUIframe.lib_sel.Bind(wx.EVT_COMBOBOX,self.callback_lib)
        ### If more buttons are added, their bindings should be added here unless in notebook pane
    def gui_setup(self):

        type_dict = {
            "string":str,
            "int": int
        }
        #OBJ.__dict__.update(self.__dict__)
        temp_dict = dict()
        #self.global_dict.
            #         defintion = self.__dict__[key]
            # if(isinstance(defintion, str)):
            #     #https://stackoverflow.com/questions/28094590/ignore-str-formatfoo-if-key-doesnt-exist-in-foo
            #     #s = Template(defintion).safe_substitute(**self.global_dict)
                # self.__dict__[key] = defintion.format_map(OBJ.global_dict) #update config file dict with globals
        for var in self.dictionary_variables:
            print(f"{var.name} is type {var.type}")
            temp_dict[var.name] = type_dict[var.type]()
            if(hasattr(var,"default")):
                temp_dict[var.name] = var.default
            #if(hasattr(var,"options")):
                
            #type_of_var = 
            #gui_option()
        self.global_dict.update(temp_dict)
    def loadTest(self,e):
        #create blank maestro view
        
        sel = self.GUIframe.config_sel.GetSelection() #Gets current combo box selection
        
        if sel != -1:  # Makes sure combo box is not empty
            self.global_dict = dict()
            self.global_dict.update({"ws":self.ws})
            #self.global_dict["DUTLIB"] = "morpheus_tests" #TEMP TODO
            
            selectectConfig = self.configs[self.GUIframe.config_sel.GetSelection()] #get config file from loaded files (or just load file)
            self.config = selectectConfig
            print("CONFIG FILE UPDATED")
            #self.maestro = maestro(self.ws,selectectConfig)
            #self.maestro.gui_setup()
            
            type_dict = {
                "string":str,
                "int": int
            }
            #temp_dict = dict()
            maestro_options_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
            tab_grid = wx.FlexGridSizer(len(selectectConfig.dictionary_variables), 2, 0, 0) #Configure Notebook ta
            tab_grid.AddGrowableCol(1)
            for var in selectectConfig.dictionary_variables:

                new_option = gui_option(maestro_options_tab,tab_grid,self.global_dict, var.name,var.default)
                print(f"{var.name} is type {var.type}")
                self.global_dict[var.name] = type_dict[var.type]()
                if(hasattr(var,"default")):
                    self.global_dict[var.name] = var.default
                if(hasattr(var,"options")):
                    #print(eval(var.options))
                    print(self.global_dict)
                    try:
                        new_option.global_dict = self.global_dict
                        new_option.option_exp = var.options
                        new_option.options = eval(var.options.format(**self.global_dict))
                    except:
                        pass
                new_option.plan()
                maestro_options_tab.options.append(new_option)
            maestro_options_tab.tab_grid = tab_grid
            maestro_options_tab.build(self.GUIframe.testbench_tabs,"maestro options")
            self.maestro_options_tab = maestro_options_tab
                #type_of_var = 
                #gui_option()
            #self.global_dict.update(temp_dict)
            #self.openNewTab(self.maestro.global_dict)
            #loadFromObj
            #maestro_options_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
            ##maestro_options_tab.loadFromObj(self.maestro.global_dict)
            #maestro_options_tab.build(self.GUIframe.testbench_tabs,"maestro options")


    def openNewTab(self, obj_to_tab):

        tab_name = "test tab"
        new_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
        new_tab.build(obj_to_tab,self.GUIframe.testbench_tabs)
    
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
    def callback_lib(self,e):
        selectedLib = self.libList[self.GUIframe.lib_sel.GetSelection()]
        print(f"lib_sel updated to {selectedLib}")
        self.lib =selectedLib
    def populateLibraries(self):

        '''Function used to populate library drop down'''

        self.libList = [lib.name for lib in self.ws.dd.GetLibList()] #Get list of available libraries

        self.GUIframe.lib_sel.AppendItems(self.libList) #Append to drop downs
        self.GUIframe.lib_sel.AppendItems(self.libList) 

    
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
        print("MAKE TEST")
        print(self.global_dict)
        #print("DUTLIB is {DUTLIB}".format(**self.global_dict))
        
        self.maestro = maestro(self.ws,self.config,self.lib,self.global_dict)
        try:
            self.maestro.open()
            self.maestro.build = True
            self.maestro.createTests() #replace to build
        except:
            TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)

            pass
        try:
            self.schematic_view()
        except:
            
            pass
        self.maestro.close()
        #self.maestro.build()

    def schematic_view(self):
        schematic_view_tab = TabTemplate(self.GUIframe.testbench_tabs, wx.ID_ANY)  #Create tab using the TabTemplate Class
        schem = self.maestro.schematics[self.maestro.schematic]

        tab_grid = wx.FlexGridSizer(len(schem.terminals_dict), 2, 0, 0) #Configure Notebook ta
        tab_grid.AddGrowableCol(1)
        for terminal in schem.terminals_dict:

            new_option = gui_option(maestro_options_tab,tab_grid,self.global_dict, var.name,var.default)
            print(f"{var.name} is type {var.type}")
            self.global_dict[var.name] = type_dict[var.type]()
            if(hasattr(var,"default")):
                self.global_dict[var.name] = var.default
            if(hasattr(var,"options")):
                #print(eval(var.options))
                print(self.global_dict)
                try:
                    new_option.global_dict = self.global_dict
                    new_option.option_exp = var.options
                    new_option.options = eval(var.options.format(**self.global_dict))
                except:
                    pass
            new_option.plan()
            maestro_options_tab.options.append(new_option)
        maestro_options_tab.tab_grid = tab_grid
        maestro_options_tab.build(self.GUIframe.testbench_tabs,"maestro options")
        self.maestro_options_tab = maestro_options_tab


    #TODO Modify so the bulk of the "re-evaluation" function takes place within the Schematic file
    def reevaluate(self,e):

        '''Reevaulate function to rebuild test schematic from user input'''

        cs = self.GUIframe.testbench_tabs.GetSelection()
        schem = self.schems[cs]
        schem.reevaluate(self.testPins[cs])


    def refresh_options(self,e):
        for option in self.maestro_options_tab.options:
            option.update_options()
   # def statusPrint(self, msg):
   #     self.GUIframe.StatusBar.SetStatusText(0,msg);
    

    #TODO error collection function
    def error(self, e):
        #error = self.MEH.catch(e)
        #self.GUI.raiseError(error)
        pass