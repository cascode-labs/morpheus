from morpheus.Config import *
from morpheus.Schematic import *
from morpheus.Formatter import moprheus_Formatter

from morpheus.MorpheusObject import morpheusObject
from morpheus.MorpheusDict import morpheusDict
#List of properties to remove from save
maestro_properties_to_remove =[
    "ws", "session", "asi_session", #change based on cadence session
    "equationDict", #TODO REMOVE not needed anymore
    "config" #TDOD remove not needed anymore
]
logger = logging.getLogger("morpheus")

class maestro(morpheusObject):#test
    def __init__(self,ws,config,lib="", global_dict = dict()) -> None:
        self.ws = ws
        self.lib = lib
        self.config = config
        self.global_dict = morpheusDict(global_dict)

        #DEFAULTS
        self.build = False
        self.cell = "Morpheus_Testbench"
        self.view = "maestro"

        self.overwrite_maestro = False
        self.overwrite_schematic = False
        self.schematics = dict()

        self.equationDict = {
            "DUT" : "DUT" #test.schem.DUT.name
        }

        config.updateInstance(self)# load config file

        #self.options = [self.overwrite_maestro,self.overwrite_schematic]
        
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
            sconfig = config(testConfig.schematic,config_types.SCHEMATIC)#find the config file for the schematic
            
            #FIX!!!!!!!!!
            sconfig.cell = self.cell#TODO

            schem = schematic(self.ws, sconfig, self.lib, self.global_dict)#check if exists as well
            schem.cell = self.cell
            if(self.build): #build (even if overwriting) in build mode
                schem.plan()
                schem.build()
            self.schematics.update({testConfig.schematic:schem})
        return schem

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
            #self.createDictFromSchem(self.config)
            #schematic = self.getSchematic(test)
            self.createTest(self.config) 
        else: #MULTITEST TODO
            for test in self.config.tests: #create all tests in the test config
                #self.createDictFromSchem(test)
                #schematic = self.getSchematic(test)
                self.createTest(test) 
        #add variables (TODO break into new function)
        for var in self.config.variables: 
            self.ws.mae.SetVar(var.name.format(**self.equationDict),var.value,typeValue=var.test, #Attach varaibles to Maestro view
                                session=self.session)
        #add corners
            #self.createCorners()
    def createTest(self,test):
            schem = self.getSchematic(test)
            setattr(test,"schem",schem)
            logger.info("create test {test}\n".format( test= test.name))
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
           # if(hasattr(test,"ocean")):   
            #    self.createOceanScripts(test)
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
        #search dictionary for type
        string_split = equation.type.split(".")
        dictionary_definition = morpheusDict(self.global_dict.copy())
        #dictionary_definition = equation.type.format(**dictionary_definition) 
        #dictionary_definition = dictionary_definition[equation.type.format(**dictionary_definition)]

        # for iterable in dictionary_definition:
            
        #     tempDict = self.global_dict.copy() #MAKE COPY
            # string_split = equation.type.split(".")
            # dictionary_definition = self.global_dict.copy()
            # for string in string_split:
            #     if(type(dictionary_definition) is dict):
            #         dictionary_definition = dictionary_definition[string]
            #     else:
            #         dictionary_definition = dictionary_definition.__dict__[string]
            # tempDict.update({equation.type:iterable}) #TODO add linked varriables
            # #expression = equation.equation.format(**tempDict) 
            # formatter = moprheus_Formatter()
            # expression = formatter.format(equation.equation,**tempDict) 
            # name = equation.name.format(**tempDict)
        formatedequations = test.schem.global_dict.formatObjStrings(equation)
        formatedequations = self.global_dict.formatString(equation)

        for equation in formatedequations:
            self.ws.mae.AddOutput(equation.name,test.name, session = self.session,expr = equation.expression)#TODO CHECK IF EXISTS AND UPDATE

        # if(self.equationDict.get(equation.type) is not None):
        #     for pin in self.equationDict.get(equation.type):#TODO MOVE FOR LOOP TO CREATE EQUATIONS?!?!
        #         tempDict = self.global_dict.copy() #MAKE COPY
        #         tempDict.update({equation.type:pin}) #TODO add linked varriables
        #         expression = equation.equation.format(**tempDict) 
        #         name = equation.name.format(**tempDict)
        #         self.ws.mae.AddOutput(name,test.name, session = self.session,expr = expression)#TODO CHECK IF EXISTS AND UPDATE

     #def recursiveFormat():
    def createOceanScripts(self,test):
        for script in test.ocean: #create all requred scripts
            self.createOceanScript(test, script)

    def createOceanScript(self,test,script):
        #self.x_mainSDB
        #window = self.ws.axl.GetWindowSession()
        #form = self.ws.__.axlOutputsForm28
        num = re.findall(r'\d+', self.session)[0]

        #form = getattr(self.ws.__,"axlOutputsForm"+num)

        my_globals = self.ws.globals("")
        self.ws["morpheus_maeAddOceanMeasurement"](self.session)
        #form = self.ws['axlOutputsForm'+ num]
        #widtget =  self.ws["symeval"](form,"axlOutputsWidget"+num)
        widtget= "axlOutputsWidget" + num  #"axlOutputsForm"+num+"->"+"axlOutputsWidget" + num
        self.ws["_axlOutputsSetupAddOutputByType"](widtget, "ocean", test.name)
        self.ws["describe"](form)
        form = self.ws.__['axlOutputsForm'+num]
        #print(dir(form))
        #print(form._attributes)
        #widtget = self.ws.__['axlOutputsForm'+num]['axlOutputsWidget'+num]
        self.ws["_axlOutputsSetupAddOutputByType"](widtget, "ocean", test.name)
        self.ws["_axlOutputsSetupAddOutputByType(axlOutputsForm"+num+"axlOutputsForm"+num+"->"+"axlOutputsWidget" + num+ "'ocean' '"+test.name+"')"]
        #self.ws["_axlOutputsSetupAddOutputByType"](getattr(getattr(my_globals, "axlOutputsForm"+num), "axlOutputsWidget"+num), "ocean", test.name)


        self.ws["print"]("hello")
#_axlToolSetOutputExpr("SESSION" "TESTNAME" 16 "SCRIPT LOCATION")
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
        #self.equationDict.update({"DUT":schematic.DUTname}) #add linked varriables

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


    def save(self):

        state =self.__getstate__()

        with open('savetesting_test0.yml', 'w') as yaml_file:
            yaml.dump(self, yaml_file, default_flow_style=False,sort_keys=False)
        pass

    def saveMaestroAsYML(self):
        #save TESTS
        self.x_mainSDB = self.ws.axl.GetMainSetupDB( self.session )
        curr_tests = self.ws.axl.GetTests(self.x_mainSDB)
        for test in curr_tests[1]:
            #if(type(test) == int):
             #    continue

            #save SIM OPTIONS
            sim_options = self.ws.mae.GetSimOption(test,session = self.session)
            #save HIGH PERFORMANCE SIM OPTIONS
            #print()
            #asiDisplayHighPerformanceOption(asiGetTool('spectre))
            tool = self.ws.asi.GetTool('spectre')
            logger.info("test data loaded")

            #high_sim_options = self.ws.asi.GetHighPerformanceOptionVal(self.asi_session, varName)
            
            
            #save ANALYSISES
            
            #maeGetAnalysis
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
            logger.info(f"{var.name} is type {var.type}")
            temp_dict[var.name] = type_dict[var.type]()
            if(hasattr(var,"default")):
                temp_dict[var.name] = var.default
            #if(hasattr(var,"options")):
                
            #type_of_var = 
            #gui_option()
        self.global_dict.update(temp_dict)