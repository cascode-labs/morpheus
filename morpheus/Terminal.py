from morpheus.Config import config
from morpheus.Config import config_types
import re

class Terminal:
    terminals = dict()
    instances = dict()
    def __init__(self,pin) -> None: #for pin terminals
        self.eval  = False
        self.type = None
        self.label = pin.name
        self.dictionary = dict()
        self.dictionary["name"] = pin.name
        pass
    def update(self, pin,pinslist = None):
        if(pinslist): #has multiple pins
            self.pinslist = pinslist
            num = 0
            for pin_PL in self.pinslist:
                self.dictionary["pin" + str(num)] = pin_PL.name #add all pins to dictionary
                num+=1
             
        self.net = self.label
        if(hasattr(pin,"type")): self.type = pin.type
        if(hasattr(pin,"region")):self.region = pin.region #check
        self.term = pin
        self.config = Terminal.getTerminal(pin)
        self.width = self.config.width
        self.height = self.config.height
        self.eval = True
        #if(self.type == 'gnd'):
        #    self.net = 'gnd!'
        if(hasattr(self.term, "label")):
            self.net = self.term.label
        #if(hasattr(self.term, "net")):
        #    self.net = self.term.net

    def plan(self,position):
        self.position = position
    def getInst(ws,inst): #TODO use dict to load terminals only once
        instance = Terminal.instances.get(inst.name)
 
        if  instance is None:
            print("Skill loading " + inst.name)
            instance = ws.db.OpenCellViewByType(inst.lib, inst.name, "symbol")
            Terminal.instances.update({inst.name: instance})
        return instance

    def build(self,ws,cv,dir):
        #TODO add special case for no connect
        if(self.term.term == "NOCONNECT"):
            name = self.label + "_NOCONN"
            rt =ws.db.ConcatTransform([[0,0],dir[0]],[[0,0],"R90"])
            instance = ws.db.OpenCellViewByType("basic", "noConn", "symbol")
            ws.db.CreateInst(cv, instance, name, dir[1][1], rt[1],1)
        else:
            for inst in self.config.Insts:
                    #add position of terminal location to instance definition
                if(not(isinstance(inst.position[0],int))): #for wires or other things with multiple position points
                    position = [[e1[0] + self.position[0], e1[1] + self.position[1]] for e1 in inst.position] #update all positions values
                else: #standard location change (1 point)
                    x = inst.position[0] + self.position[0]
                    y = inst.position[1] + self.position[1]
                    position = [x,y]

                if(inst.name == "wire"): #WIRE SPECIAL CASE
                    mywire = ws.sch.CreateWire(cv, "draw", "full", position, 0.0625, 0.0625, 0.0)
                    if(hasattr(inst,"label") and hasattr(self,"label")):
                        ws.sch.CreateWireLabel(cv, mywire[0], [position[0][0] + 0.0325,position[0][1] + 0.05], inst.label.format(**self.dictionary), "upperLeft", "R90", "stick", 0.0625, False)
                else:
                    symbol = Terminal.getInst(ws,inst)
                    name = self.config.name + "_" + inst.name #TODO BETTER NAMING SYSTEM
                    if(hasattr(self,"label")):
                        name = inst.instance.format(name = self.label) #named based on instance and terminal label
                    #START CREATING PROPERTIES
                    prop = list() 

                    if(hasattr(inst,"parameters")): #SET PROPERTIES!
                        for param in inst.parameters.__dict__:#defaults for each inst
                            property = inst.parameters.__dict__.get(param).format(name = self.label)
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
                    new_inst = ws.db.CreateParamInst(cv, symbol, name, position, rotation,1,prop) #create instance with parameters
            #end For Loop per Instance
        #end For Loop per Terminal
    def getTerminal(term_type):
        terminal = Terminal.terminals.get(term_type.term)
 
        if terminal is None:
            terminal = config(term_type.term, config_types.TERMINAL)
            Terminal.terminals.update({term_type.term:terminal})

        return terminal