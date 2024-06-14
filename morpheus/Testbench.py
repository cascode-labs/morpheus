#
#
# The testbench class contains all the editing portion of the cadence views.
# This includes the SCHEMATIC and MAESTRO classes 
# The testbench is responsible for managing these classes and their subclasses

class testbench:
    def __init__(self,  ws,   lib,   DUT,   config=None) -> None:
        self.DUT = DUT
        self.ws = ws
        self.lib = lib
        self.cell = DUT.cell_name + "_AUTO_TB"
        
        self.schematic = None
        self.maestro = None
        self.pin_list = None

    def GUI_Menu(): #method for handling the gui
        pass

    def loadConfigFile(self,Config configFile):

        self.equationDict = {
            "DUT" : "DUT" #test.schem.DUT.name
        }

        self.open() #TODO delete? become part of GUI Handler
        self.schematics = dict()
        if(test):
            schem = self.getSchematic(test) #TODO should run in create test not before
            self.createTest(test,schem)


    @staticmethod
    def createMaestroView(ws,dut_lib,dut_cell,tb_lib):
        pass

    def load_schematic():
    pass
    
    #Using config file build the testbench from scratch
    def build():
        #self.schematic.

    #Try and find save file, if not then try and import testbench from cellviews
    def load():
    
    #save current testbench and parts in YML format
    def save():


