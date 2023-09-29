from morpheus.Config import *
from morpheus.Schematic import *

class maestro:
    def __init__(self,ws,lib,DUT) -> None:
        self.DUT = DUT
        self.ws = ws
        self.lib = lib
        self.cell = DUT.cell_name + "_AUTO_TB"

        self.equationDict = {
            "DUT" : "DUT" #test.schem.DUT.name
        }

        self.open() #TODO delete? become part of GUI Handler
        self.schematics = dict()


    @staticmethod
    def createMaestroView(ws,dut_lib,dut_cell,tb_lib):

        '''Generate MaestroView for a given DUT cell'''

        DUT = ws.db.OpenCellViewByType(dut_lib,dut_cell, "symbol")
        
        return maestro(ws,tb_lib,DUT)

    def getSchematic(self,test):
        schem = self.schematics.get(test.schematic)
        if(schem is None): #doesnt exist
            sconfig = config("Schematics/{filename}.yml".format(filename = test.name))
            schem = schematic(self.ws,self.lib,self.DUT,sconfig,test)
            schem.evaluate()
            #
            schem.plan()
            schem.build()
            self.schematics.update({test.schematic:schem})
        return schem
    
    def createConfig(self,Config):
        config_view = self.ws.hdb.Open(self.lib, self.cell, "config_" + Config.name, "a", "CDBA")
        self.ws.hdb.SetTopCellViewName(config_view, self.lib, self.cell, Config.schematic)
        self.ws.hdb.SetDefaultLibListString(config_view, "myLib")
        self.ws.hdb.SetDefaultViewListString(config_view, "spectre schematic veriloga")
        self.ws.hdb.SetDefaultStopListString(config_view, "spectre")
        self.ws.hdb.Save(config_view)
        self.ws.hdb.Close(config_view)

    def createTest(self,Config,schem):
        
        for test in Config.tests:
            setattr(test,"schem",schem)
            self.ws.mae.CreateTest(test.name, session = self.session, # Create Test within Maestro
                                   lib = self.lib, cell = self.cell, view = "config_" + Config.name)
            
            self.ws.mae.SetAnalysis(test.name, test.analysis.type , #Add Test Analysis within Maestro
                                    session = self.session, options = test.analysis.options)

            self.x_mainSDB = self.ws.axl.GetMainSetupDB( self.session )

            self.ws.sev.AddExpression(self.session,"ocean","")
            #self.createCorners(test)
            self.createSignals(test)
            self.createEquations(test)
            #self.addOceanScripts(test)

        for var in Config.variables:
            
            self.ws.mae.SetVar(var.name.format(**self.equationDict),var.value,typeValue=var.test, #Attach varaibles to Maestro view
                               session=self.session)
            

        
        self.close()



    def createCorner(self,corner): #TODO Not finished
        #if(self.PWL):
        filepath = "default"
        newCorner = self.ws.axl.PutCorner(self.x_mainSDB, corner.name)
        #ADD ALL CORNER VARIABLES
        self.ws.axl.PutVar(newCorner, "DATA_path", filepath)# ADD DATA FILE PATH
        self.ws.axl.PutVar(newCorner, "CLK_path", filepath)# ADD DATA FILE PATH
        self.ws.axl.PutVar(newCorner, "VIO_path", filepath)# ADD DATA FILE PATH

    def createEquations(self, test):
        for equation in test.equations:
            self.createEquation(test, equation)
    def createEquation(self, test, equation):
        
        self.createEquDict(test,equation)

        name = equation.name.format(**self.equationDict)
        self.ws.mae.AddOutput(name,test.name, session = self.session,expr = equation.equation.format(**self.equationDict))

    def createSignals(self,test):
        for signal in test.signals: #create all requred signals
            self.createSignal(test, signal)

    def createSignal(self, test, signal):
        
        if hasattr(signal,"type"):
            self.createEquDict(test,signal)
        
        self.ws.mae.AddOutput(signal.name,test.name, session = self.session,outputType ="net",signalName = signal.signal.format(**self.equationDict))

    def createEquDict(self,test, data):
        pins_of_type = [pin for pin in test.schem.evaluatedPins if pin.type == data.type]
        for pin in pins_of_type:
            self.equationDict.update({data.type: pin.label})
            #format equation string with dict
            name = data.name.format(**self.equationDict)

 
    def addOceanScript(self,test,script):
        pass#self.ws.axl.WriteOceanScriptLCV(script,self.lib,self.cell,"maestro")

    def simulate(self):
        pass
    
    def open(self):
        self.session = self.ws.mae.OpenSetup(self.lib, self.cell,"maestro") #create new maestro view
        
    def close(self):
        self.ws.mae.SaveSetup(session = self.session)
        self.ws.mae.CloseSession(session = self.session)