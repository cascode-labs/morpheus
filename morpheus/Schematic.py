from morpheus.Config import *
import re
import copy
import math
from morpheus.Exceptions.SelectionBox import SelectionBoxException

from morpheus.Terminal import Terminal
class DUT_pin:
    def __init__(self,pin) -> None:
        self.eval  = False
        self.pin  = pin
        self.label = pin
        self.type = ""
    
class schematic:
    def __init__(self,ws,lib,DUT,config, tconfig) -> None:
        self.DUT = DUT
        self.ws = ws
        self.tconfig = tconfig
        self.config = config
        self.lib = lib
        self.terminals = dict()
        self.instances = dict()
        self.evaluatedPins = list()
        if(hasattr(self.config,"Build")):
            self.config.Build = list()

    def reevaluate(self, pins):
        self.evaluatedPins = pins

        cvid = self.ws.dd.GetObj(self.lib,self.DUT.cell_name + "_AUTO_TB","schematic_" + self.config.name) #delete
        #self.maestro.createEquations()

        self.ws.dd.DeleteObj(cvid) #delete
        self.plan()
        self.build()

    def getInst(self,inst): #TODO use dict to load terminals only once
        instance = self.instances.get(inst.name)
 
        if  instance is None:
            print("Skill loading " + inst.name)
            instance = self.ws.db.OpenCellViewByType(inst.lib, inst.name, "symbol")
            self.instances.update({inst.name: instance})
        return instance

    def getTerminal(self,term_type): #TODO use dict to load terminals only once
        terminal = self.terminals.get(term_type.term)
 
        if terminal is None:
            terminal = config("Terminals/" + term_type.term + ".yml")
            self.terminals.update({term_type.term:terminal})

        
        return terminal
    def evaluate(self):
        #match pin names to terminals defined in the PLAN section of schematic config
        #for(term in self.config.Build):
            
        for pin in self.DUT.terminals: 
            inst = DUT_pin(pin.name) #contains default values
            term = Terminal(pin)
            for pin_type in self.config.Terminals:
                if(re.search(pin_type.pattern,pin.name) != None): #use RegEx to find if the pin matches the pin_type
                    
                    term.update(pin_type)#,term_type)
                    #CHECK IF SHOULD BREAK (one pin multiple terminals?)
                    break;
            self.evaluatedPins.append(term)


    def plan(self): #USED TO CALCULATE LOCATIONS OF TERMINALS IN PLAN
        max_region = 4
        if(hasattr(self.config,"Build")):
            self.Build = self.config.Build
        else:
            self.Build = list() #reset build list (look at (and append) Config Build?)
        #create Dict for all pin types in schematic
        pin_types = {self.config.Terminals[i].type: self.config.Terminals[i] for i in range(len(self.config.Terminals))} 
        #only plan pins that have been evaluated
        valid_pins = [pin for pin in self.evaluatedPins if pin.eval]
        for pin in valid_pins:
            pin_type = pin_types.get(pin.type)
            self.Build.append(pin)
        
        #go back and calculate sizing per regions
        region_removed = [i for i in self.Build if hasattr(i,"region")] #only terminals that have regions
        box = self.DUT.b_box
        region_max_height = abs((box[1][0]) - (box[1][1]))+3#self.DUT
        region_max_width = abs((box[0][0]) - (box[1][0]))
        for i in range(max_region):
            region_sorted = list(filter(lambda x: x.region == i, region_removed))
            MAX_OBJ=len(region_sorted)
            x_offset = 0
            y_offset = 0
            box_w = 0
            box_h = 0
            avail_w = 0
            avail_h = 0
            avail_x = 0
            avail_y = 0
            ratio = 8
            x = 0
            y = 0
            while(len(region_sorted) > 0):
                #if(avail_h > .1):
                
                if(box_w <= box_h*ratio):
                    region_sorted = sorted(region_sorted, key=lambda x: x.height, reverse=False)
                   
                else:
                    region_sorted = sorted(region_sorted, key=lambda x: x.width, reverse=False)
                    x = 0
                    y += term.height #TODO
                term = region_sorted.pop()

                box_w = max(x,box_w)
                box_h = max(y,box_h)
                #x = box_w #TODO
                #avail_h = 
               
                term.plan([x,y])

                x += term.width
            region_max_height = max(region_max_height,box_h)
            region_max_width = max(region_max_width,box_w)
        count = 0
        
        #TODO FIX REGIONS TO USE INFINITE REGIONS IN FORMAT (3x3,4x4,5x5,etc.)
        #only move around planned terminals TODO change back to region as all regions terminals should be planned
        #comment region_removed = [i for i in self.Build if hasattr(i,"planned")]
        rows = round(math.sqrt(max_region))
        height = region_max_height
        width = region_max_width
        #add region sizing
        for region in range(max_region):
            region_sorted = list(filter(lambda x: x.region == region, region_removed))
            x = (region%rows)*width #TODO
            y = math.floor(region/rows)*height #TODO

            for term in region_sorted:
                
                term.position[0] = term.position[0] + x #TODO
                term.position[1] = term.position[1] - y #+ region*3
                count +=1


        #TODO add bounding box type for building

   

    
    #place all terminals in schematic
    def build(self):
        ws= self.ws
        terminals = self.terminals

        print("Building!")
        #create cell view for schematic
        cv = self.ws.db.OpenCellViewByType(self.lib, self.DUT.cell_name + "_AUTO_TB","schematic_" + self.config.name, "schematic", "w")
        if(cv is None): #TODO CREATION EXCEPTIONS
            print("Error: Schematic not found. Check if open elsewhere")
            return
        self.cv = cv #unnecissary
        
        box = self.DUT.b_box
        x= -8 + (box[1][0])
        y= -6 - (box[0][1])
        dut_inst = ws.sch.CreateInst( cv, self.DUT, "DUT", [x,y], "R0") #place DUT TODO add code to check bounding box

        #RUN THROGUTH ALL TERMINALS
        for terminal in self.Build: #TODO add check not to load the same master twice
            pin = [p for p in self.DUT.terminals if hasattr(terminal,"label") and p.name == terminal.label]
            if(len(pin)>0):
                dir = self.createWireForFloatingInstPin(cv,dut_inst, pin[0] ,terminal.net)
                #self.ws['CCSCreateWireForFloatingInstPin'](cv,dut_inst, pin[0] ,terminal.label) #TODO make work with no pin heads (also make part of python rather than skill)
            terminal.build(ws,cv,dir)

        if(hasattr(self.tconfig, 'scriptpath')): #If custom script is provided, run the script
            ws['load'](self.tconfig.scriptpath)
            ws[self.tconfig.script](cv)


        ws.db.Check(cv) 
        ws.db.Save(cv)
        ws.db.Close(cv)
    #end build
    
    #ported from skill
    def createWireForFloatingInstPin(self,cv,inst,ter,myLabel): #TODO fix issue with no pin wires
        instTermbBox = self.ws.db.TransformBBox(ter.pins[0].fig.bBox, inst.transform)

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
            selBox = [pin for pin in inst.master.shapes if pin.lpp == ['instance', 'drawing'] ]
            ibox=self.ws.ge.TransformUserBBox(selBox[0].b_Box, inst.transform)
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
        self.ws.sch.CreateWireLabel(self.cv , mywire[0], [lab_x,lab_y], myLabel, "upperLeft" ,dir ,"stick" ,0.0625 ,True)
        return [dir,wireDir]
