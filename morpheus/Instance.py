
from morpheus.Config import *
import re
import copy
import math
import logging
from morpheus.Exceptions.SelectionBox import SelectionBoxException
from morpheus import Config
from string import Template
from morpheus.Terminal import Terminal


class FailsafeDict(dict):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return "{" + str(item) + "}"
        # end try
    # end def
# end class

class instance:
    def __init__(self, ws, config,global_dict = dict()) -> None:
            self.location = None
            self.term = None

            self.global_dict = FailsafeDict(global_dict)

            self.loadConfig(config)

            self.x_offset = 0;
            self.y_offset = 0;
            self.ws = ws #skillbridge


    def loadConfig(self,config):
        for key in config.__dict__: #GO RECURSIVELY EVENTUALLY
            defintion = config.__dict__[key]
            if(isinstance(defintion, str)):
                #https://stackoverflow.com/questions/28094590/ignore-str-formatfoo-if-key-doesnt-exist-in-foo
                #s = Template(defintion).safe_substitute(**self.global_dict)
                config.__dict__[key] = defintion.format_map(self.global_dict) #update config file dict with globals
        self.__dict__.update(config.__dict__)
    
    
    def evaluate(self):

        #create instances per terminals
        #terminals
        #device.get_matches()
        #for terminal in self.nets:
        #    instance.get_matches(self.inst.nets,"name", net.pattern)
        self.symbol = self.ws.db.open_cell_view(self.lib,self.cell,"symbol")
        self.terminals = list() #clear terminals
        if(self.terminal_types is not None): #check that is not CADENCE INSTANCE OR INSTANCE WITH NO TERMINALS TO EVALUATE
            for terminal_type in self.terminal_types: #every type of terminal
                terminal_type.matches = instance.get_matches(self.symbol.terminals,"name", terminal_type.pattern)

                #if terminal_type.term =="dc2":# temp check

                for match in terminal_type.matches: #create terminal for each match of that type
                    #if(hasattr(terminal_type,"term")): #import from config file
                    #    config = Config.config(terminal_type.term, Config.config_types.TERMINAL)#TODO REMOVE or require?
                    #else:
                    config = terminal_type
                    terminal = instance(self.ws,terminal_type,self.global_dict)
                    terminal.label = match.name
                    terminal.cadence_term = match
                    #terminal.evaluate() #Dont need to evaluate created terminals
                    self.terminals.append(terminal)

                        

                
        print("completed elvaluation on ___")
        # for terminal in self.terminals: # go through all terminals on device

        #     #import terminal config file

        #     #terminal_inst = instance(cell=)
        #     inst = DUT_pin(pin.name) #contains default values
        #     term = Terminal(pin)
        #     for pin_type in self.config.Terminals:
        #         if(re.search(pin_type.pattern,pin.name) != None): #use RegEx to find if the pin matches the pin_type
                    
        #             term.update(pin_type)#,term_type)
        #             #CHECK IF SHOULD BREAK (one pin multiple terminals?)
        #             break;
        #     self.evaluatedPins.append(term)
    def plan(self):
        if(self.term is not None): #IT IS A MORPHEUS INSTANCE NOT CADENCE
            config = Config.config(self.term ,Config.config_types.TERMINAL)
            self.loadConfig(config)
        else: #NON MORPHEUS TERMINAL/INSTANCE
        #check if location was specifed, if so. Do not build on top level
            if(self.location == None): #should be top level
                self.symbol = self.ws.db.open_cell_view(self.lib,self.cell,"symbol")
                self.calculateInstSize()
                #add wires
            for terminal in self.terminals:
                terminal.plan()
        

        pass
    def calculateInstSize(self):
        DUT_Pin_Boxs = [i.b_box for i in self.symbol.shapes if i.layer_name == "pin"]
        xMin=0
        xMax=0
        yMin=0
        yMax=0
        wireSpacing = 1

        for box in DUT_Pin_Boxs:
            xMin = min(box[1][0],xMin)
            xMax = max(box[0][0],xMax)
            yMin = min(box[1][1],yMin)
            yMax = max(box[0][1],yMax)

        max_height = (yMax-yMin) + wireSpacing*2
        max_width = (xMax-xMin) + wireSpacing*2

        self.width = max_width
        self.height = max_height
        self.y_offset = yMin - wireSpacing
        self.x_offset = xMin - wireSpacing

    def findDUT(self):
        if(self.cv.instances is not None):
            for inst in self.cv.instances:
                if inst.cell_name == self.DUT.cell_name:
                    self.DUTinst = inst #internal
                    self.DUTname = inst.name
                    return inst
        return None #none found   
    def find(self):
        if (self.location == None):
            pass
        else:
            pass

    def get_matches(list_of_objs, parameter, pattern):
        #evalutate cellview or symbol view
        #Either get nets/insts inside cellview or use symbol pins

        matching_objs = list()
        for o in list_of_objs:
            text = instance.object_parameter_get(o,parameter)
            if(re.search(pattern,text) != None): #use RegEx to find if the pin matches the pin_type
                matching_objs.append(o) #object is a match
        return matching_objs

    def object_parameter_get(obj,parameter_heir):
        parameters = parameter_heir.split(".")
        obj_rec = obj
        for parameter in parameters:
            obj_rec = getattr(obj_rec,parameter)
        return obj_rec



    def build(self,cv,dir,xoffset,yoffset,gridSize):



        oldx = self.x
        oldy = self.y
        self.cv = cv
        self.x = instance.ceilByInt(xoffset + self.x + self.width/2 - self.x_offset,gridSize)
        self.y = instance.ceilByInt(yoffset + self.y + self.height/2 - self.y_offset,gridSize)
        #TODO add special case for no connect
        if(self.term == "NOCONNECT"):
            name = self.label + "_NOCONN"
            rt =ws.db.ConcatTransform([[0,0],dir[0]],[[0,0],"R90"])
            instance = ws.db.OpenCellViewByType("basic", "noConn", "symbol")
            ws.db.CreateInst(cv, instance, name, dir[1][1], rt[1],1)
        elif(not hasattr(self,"Insts")):
            position = [self.x,self.y]
            rotation = "R0" #add rotate functionality
            prop = list() 
            self.x = instance.ceilByInt(xoffset + oldx - self.x_offset,gridSize)
            self.y = instance.ceilByInt(yoffset + oldy - self.y_offset ,gridSize)
            position = [self.x,self.y]
            new_inst = self.ws.db.CreateParamInst(cv, self.symbol, self.name, position, rotation,1,prop) #create instance with parameters
        else:
            for inst in self.Insts:
                    #add position of terminal location to instance definition
                if(not(isinstance(inst.position[0],int))): #for wires or other things with multiple position points
                    position = [[e1[0] + self.x, e1[1] + self.y] for e1 in inst.position] #update all positions values
                else: #standard location change (1 point)
                    x = inst.position[0] + self.x
                    y = inst.position[1] + self.y
                    position = [x,y]

                if(inst.name == "wire"): #WIRE SPECIAL CASE
                    mywire = self.ws.sch.CreateWire(cv, "draw", "full", position, 0.0625, 0.0625, 0.0)
                    if(hasattr(inst,"label") and hasattr(self,"label")):
                        self.ws.sch.CreateWireLabel(cv, mywire[0], [position[0][0] + 0.0325,position[0][1] + 0.05], inst.label.format(**self.__dict__), "upperLeft", "R90", "stick", 0.0625, False)
                else:
                    symbol = Terminal.getInst(self.ws,inst)
                    name = self.name + "_" + inst.name #TODO BETTER NAMING SYSTEM
                    if(hasattr(self,"label")):
                        name = inst.instance.format(**self.__dict__) #named based on instance and terminal label
                    #START CREATING PROPERTIES
                    prop = list() 

                    if(hasattr(inst,"parameters")): #SET PROPERTIES!
                        for param in inst.parameters.__dict__:#defaults for each inst
                            property = inst.parameters.__dict__.get(param).format(**self.__dict__)
                            prop.append([param,"string",property])
                        if(hasattr(self.term,"parameters")): #Terminal takes priority over default
                            for param in self.term.parameters.__dict__:
                                #TODO ERROR CATCH NUMBERS
                                propText = self.term.parameters.__dict__.get(param)
                                property = propText.format(name = self.label)
                                if propText.find("regex") != -1:
                                    property = re.sub(self.term.pattern,propText.replace("regex","") ,self.label) #Do regular expression replace
                                prop.append([param,"string",property])
                    rotation = "R0" #add rotate functionality
                    if(hasattr(inst,"rotation")):
                        rotation = "R" + str(inst.rotation)   
                    new_inst = self.ws.db.CreateParamInst(cv, symbol, name, position, rotation,1,prop) #create instance with parameters

            #end For Loop per Instance
        #end For Loop per Terminal
        self.inst = new_inst
        if(hasattr(self,"terminals")):
            for term in self.terminals:
                self.createWireForFloatingInstPin(term)
    def ceilByInt(num, base):
        return base * math.ceil(num/base)
    def createWireForFloatingInstPin(self,term): #TODO fix issue with no pin wires
        instTermbBox = self.ws.db.TransformBBox(term.cadence_term.pins[0].fig.bBox, self.inst.transform)

        xa = instTermbBox[0][0]
        xb = instTermbBox[1][0]
        ya = instTermbBox[0][1]
        yb = instTermbBox[1][1]
        x1 = (xa + xb)/2
        y1 = (ya + yb)/2
        dir = "R0"
        wireDir=[[x1,y1], [x1+0.3,y1]]
        lab_x=x1+0.04
        lab_y=y1
        try:
            selBox = [pin for pin in self.inst.master.shapes if pin.lpp == ['instance', 'drawing'] ]
            ibox=self.ws.ge.TransformUserBBox(selBox[0].b_Box, self.inst.transform)
        except IndexError:
            raise SelectionBoxException #No selection box in symbol
        

        left_E = ibox[0][0]
        right_E=ibox[1][0]
        top_E=ibox[1][1]
        bot_E= ibox[0][1]
        grid=2*self.ws.sch.GetEnv("schSnapSpacing")
        if x1-grid < left_E:
            dir="R180"
            wireDir=[[x1,y1] ,[x1-0.3,y1]]
            lab_x=x1-0.04
            lab_y=y1
        elif x1+grid > right_E:
            dir="R0"
            wireDir= [[x1,y1] ,[x1+0.3,y1]]
            lab_x=x1+0.04
            lab_y=y1
        elif y1-grid < bot_E:
            dir="R270"
            wireDir=[[x1,y1] ,[x1,y1-0.3]]
            lab_x=x1
            lab_y=y1-0.04
        elif y1+grid > top_E:
            dir="R90"
            wireDir=[[x1,y1] ,[x1,y1+0.3]]
            lab_x=x1
            lab_y=y1+0.04
        mywire=self.ws.sch.CreateWire(self.cv, "draw", "full", wireDir, 0.0625, 0.0625, 0.0)
        self.ws.sch.CreateWireLabel(self.cv , mywire[0], [lab_x,lab_y], term.label, "upperLeft" ,dir ,"stick" ,0.0625 ,False)
        return [dir,wireDir]