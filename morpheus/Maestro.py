from morpheus.Config import *
from morpheus.Schematic import *

class maestro:
    def __init__(self,ws,lib,cell,view,DUT,config, build = False) -> None:
        self.build = build #temp
        self.DUT = DUT
        self.ws = ws
        self.lib = lib
        self.cell =cell
        self.view =view
        self.equationDict = {
            "DUT" : "DUT" #test.schem.DUT.name
        }

        
        #TODO MAKE SURE TO CLOSE ON ANY ERROR. Otherwise data is lost.
        self.schematics = dict()
        self.config = config
        #if(self.config):
        #    schem = self.getSchematic(self.config) #TODO should run in create test not before
            #self.createTest(config,schem)
        if(self.build):
            self.open() #TODO delete? become part of GUI Handler 
            self.createTests() #build everything
            self.close()    #TODO SAVE STATE OF OPEN/CLOSE FOR INDIVIDUAL FUNCTIONS

    @staticmethod
    def createMaestroView(ws,dut_lib,dut_cell,tb_lib):

        '''Generate MaestroView for a given DUT cell'''

        DUT = ws.db.OpenCellViewByType(dut_lib,dut_cell, "symbol")
        
        return maestro(ws,tb_lib,DUT)

    def getSchematic(self,testConfig):
        schem = self.schematics.get(testConfig.schematic)
        if(schem is None): #schematic doesnt already exist in dictionary
            #sconfig = config("{filename}".format(filename = test.schematic),config_types.SCHEMATIC)
            sconfig = config(testConfig.schematic,config_types.SCHEMATIC)#find the config file for the schematic
            
            #FIX!!!!!!!!!
            sconfig.cell = self.cell#TODO
            sconfig.name = "schematic" #MUST FIX!

            schem = schematic(self.ws,self.lib,self.DUT,sconfig,testConfig)#check if exists as well
            if(self.build): #build (even if overwriting) in build mode
                schem.plan()
                schem.build()
            self.schematics.update({testConfig.schematic:schem})
        return schem
    
    #def getConfig(self,testConfig):


    def createConfig(self,Config):
        config_view = self.ws.hdb.Open(self.lib, self.cell, "config_" + Config.name, "a", "CDBA")
        self.ws.hdb.SetTopCellViewName(config_view, self.lib, self.cell, Config.schematic)
        self.ws.hdb.SetDefaultLibListString(config_view, "myLib")
        self.ws.hdb.SetDefaultViewListString(config_view, "spectre schematic veriloga")
        self.ws.hdb.SetDefaultStopListString(config_view, "spectre")
        self.ws.hdb.Save(config_view)
        self.ws.hdb.Close(config_view)

    def createTests(self):
        #SINGLE TEST
        if not hasattr(self.config, "tests"): #TODO not this. I don't like this.
            #schem = self.getSchematic(self.config)
            #setattr(self.config,"schem",schem)
            self.createDictFromSchem(self.config)
            self.createTest(self.config) 
        else: #MULTITEST TODO
            for test in self.config.tests: #create all tests in the test config
                self.createDictFromSchem(test)
                createTest(test) 
        #add variables (TODO break into new function)
        for var in self.config.variables: 
            self.ws.mae.SetVar(var.name.format(**self.equationDict),var.value,typeValue=var.test, #Attach varaibles to Maestro view
                                session=self.session)
        #add corners
            #self.createCorners()
    def createTest(self,test):
            schem = self.getSchematic(test)
            setattr(test,"schem",schem)
            print("create test {test}\n".format( test= test.name))
            self.ws.mae.CreateTest(test.name, session = self.session, # Create Test within Maestro
                                   lib = self.lib, cell = self.cell, view = test.schem.view)

            if not isinstance(test.analysis, list):
                test.analysis = [test.analysis]
            for analysis in test.analysis:
                self.ws.mae.SetAnalysis(test.name, analysis.type , #Add Test Analysis within Maestro
                                    session = self.session, options = analysis.options)

            if(hasattr(test,"sim_options")): #sim options
                self.ws.mae.SetSimOption(test.name,session = self.session, options = test.sim_options)
            
            self.asi_session = self.ws.mae.GetTestSession(test.name)
            if(hasattr(test,"high_sim_options")): #sim options
                for option in test.high_sim_options:
                    if(len(option) <2): continue #skip bad options
                    [varName, val] = option
                    self.ws.asi.SetHighPerformanceOptionVal(self.asi_session, varName,val)
            
            self.x_mainSDB = self.ws.axl.GetMainSetupDB( self.session )

            #self.ws.sev.AddExpression(self.session,"ocean","") #ocean scripts broken
            
            if(hasattr(test,"corners")): #add corners if present
                self.createCorners(test)
                
            if(hasattr(test,"signals")):
                self.createSignals(test)
                
            if(hasattr(test,"equations")):   
                self.createEquations(test)
            #self.addOceanScripts(test)


    def createCorners(self, test):
        for corner in test.corners: #create all corners for maestro view
            self.createCorner(corner)
    
    def createCorner(self,corner):
        #if(self.PWL):
        newCorner = self.ws.axl.PutCorner(self.x_mainSDB, corner.name)
        #ADD ALL CORNER VARIABLES
        if(hasattr(corner,"vars")):
            for var in corner.vars:
                self.ws.axl.PutVar(newCorner, var.name, var.value)
            
    def createEquations(self, test):

        for equation in test.equations:
            self.createEquation(test, equation)
    def createEquation(self, test, equation):
        #creates equation for all of same type
        #if hasattr(equation,"type"):
        #    self.createEquDict(test,equation)
        #if type is an array then sweep those values but for now assume 1 sweeping pin type.
        if(self.equationDict.get(equation.type) is not None):
            for pin in self.equationDict.get(equation.type):#TODO MOVE FOR LOOP TO CREATE EQUATIONS?!?!
                tempDict = self.equationDict.copy() #MAKE COPY
                tempDict.update({equation.type:pin}) #TODO add linked varriables
                expression = equation.equation.format(**tempDict) 
                name = equation.name.format(**tempDict)
                self.ws.mae.AddOutput(name,test.name, session = self.session,expr = expression)#TODO CHECK IF EXISTS AND UPDATE

     #def recursiveFormat():


    def createSignals(self,test):
        for signal in test.signals: #create all requred signals
            self.createSignal(test, signal)

    def createSignal(self, test, signal):
        if(self.equationDict.get(signal.type) is not None):
            for pin in self.equationDict.get(signal.type):#TODO MOVE FOR LOOP TO CREATE SIGNALS?!?!
                tempDict = self.equationDict.copy() #MAKE COPY
                tempDict.update({signal.type:pin}) #TODO add linked varriables
                expression = signal.signal.format(**tempDict) 
                name = signal.name.format(**tempDict)
                signal_type = "net"
                if(hasattr(signal, "signal_type")):
                    signal_type = signal.signal_type
                #self.ws.mae.AddOutput(name,test.name, session = self.session,expr = expression)#TODO CHECK IF EXISTS AND UPDATE
                self.ws.mae.AddOutput(name,test.name, session = self.session,outputType = signal_type,signalName = expression)

    def createDictFromSchem(self,test): #auto run after loading schem
        schematic = self.getSchematic(test)
        #add pintypes
        #Error in finding DUT inst despite building?
        #schematic.findDUT() #cant run without error
        self.equationDict.update({"DUT":schematic.DUTname}) #add linked varriables

        for pin in schematic.evaluatedPins:
            if pin.type is not None:
                if pin.type not in self.equationDict:
                    self.equationDict.setdefault(pin.type, []) #initialize array
                self.equationDict[pin.type].append(pin.label) #TODO Independent per test!


    def createEquDict(self,test, data):#TODO add pins despite if none
        schematic = self.getSchematic(test)
        pins_of_type = [pin for pin in schematic.evaluatedPins if pin.type == data.type]
        for pin in pins_of_type:
            self.equationDict.update({data.type: pin.label})
            #format equation string with dict
            name = data.name.format(**self.equationDict)

 
    def addOceanScript(self,test,script):
        pass#self.ws.axl.WriteOceanScriptLCV(script,self.lib,self.cell,"maestro")

    def simulate(self):
        pass
    
    def open(self):
        if(self.build): #if build then destroy (TODO rename to clean build?)
            self.session = self.ws.mae.OpenSetup(self.lib, self.cell,self.view,mode="w") #create new maestro view and overwrite old one
        else:
            self.session = self.ws.mae.OpenSetup(self.lib, self.cell,self.view,mode="a")
    def close(self):
        self.ws.mae.SaveSetup(session = self.session)
        self.ws.mae.CloseSession(session = self.session)

