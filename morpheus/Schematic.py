from morpheus.Config import *
import re
import copy
import math
import logging
from morpheus.Exceptions.SelectionBox import SelectionBoxException

from morpheus.Terminal import Terminal

logger = logging.getLogger(__name__)

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
        self.gridSize = self.ws.sch.GetEnv("schSnapSpacing") #used for snapping everything to grid

        self.evaluatedPins = list()
        if(hasattr(self.config,"cell")):
            self.cell = self.config.cell
        else:
            self.cell = self.DUT.cell_name + "_AUTO_TB"
        if(hasattr(self.config,"Build")):
            self.config.Build = list()
        #set schematic view name
        if(hasattr(self.config,"name")):
            self.view = self.config.name
        else:
            self.view = "schematic_" + self.DUT.cell_name 
        #check if view already exists
        cvid = self.ws.dd.GetObj(self.lib,self.cell,self.view) #delete
        self.evaluate()#always evaluate 
        #No reason not to?
        if(cvid is None):
            #just build?
            pass
        else:
            self.cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "a") #appendmode. DONT DELETE WORK
            self.findDUT()#potential break if no DUT TODO fix
            ws.db.Close(self.cv)
            #check if open and give warning if so

        #cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "w")
        #if(cv is None and cvid is not None): #TODO CREATION EXCEPTIONS
        #    logger.error("Cannot build schematic because schematic not found. Check if open elsewhere")
        #    print("Error: Schematic not found. Check if open elsewhere")
        #    return

#load schematic from file or use import if doesnt exist
    #def load(self,config):
        #read config file
        
        #Import instead


#save schematic configuration into yml file
    #def save(self):
    #def find_DUT(self, pins):


    def reevaluate(self, pins):
        self.evaluatedPins = pins

        cvid = self.ws.dd.GetObj(self.lib,self.cell,self.view) #delete
        
        #self.maestro.createEquations()

        self.ws.dd.DeleteObj(cvid) #delete
        
        self.plan()
        self.build()

    def getInst(self,inst): #TODO use dict to load terminals only once
        instance = self.instances.get(inst.name)
 
        if  instance is None:
            logger.info("Skill loading " + inst.name)
            print("Skill loading " + inst.name)
            instance = self.ws.db.OpenCellViewByType(inst.lib, inst.name, "symbol")
            self.instances.update({inst.name: instance})
        return instance

    def getTerminal(self,term_type): #TODO use dict to load terminals only once
        terminal = self.terminals.get(term_type.term)
 
        if terminal is None:
            terminal = config(term_type.term,config_types.TERMINAL)
            self.terminals.update({term_type.term:terminal})

        
        return terminal
    

    def evaluate(self):
        #match pin names to terminals defined in the PLAN section of schematic config
        #for(term in self.config.Build):
        logger.info("Starting evaulation for DUT pins")    
        for pin in self.DUT.terminals: 
            inst = DUT_pin(pin.name) #contains default values
            term = Terminal(pin)
            for pin_type in self.config.Terminals:
                if(re.search(pin_type.pattern,pin.name) != None): #use RegEx to find if the pin matches the pin_type
                    
                    term.update(pin_type)#,term_type)
                    #CHECK IF SHOULD BREAK (one pin multiple terminals?)
                    break;
            self.evaluatedPins.append(term)


        if(hasattr(self.config,"Modules")): #config has modules
            logger.info("Starting evaulation for modules")  
            for module in self.config.Modules:
                pinslist= list()
                pinnum = 0
                for subpin in module.pins:
                    DUTpin = None
                    for pin in self.DUT.terminals:  #Use pattern to find DUTpin (TODO: upgrade to nets instead)
                        if(re.search(subpin.pattern,pin.name) != None):
                            DUTpin = pin
                            break
                           
                    
                        
                    if(not DUTpin):
                        logger.warning("Could not find pin ", pinnum ," for ", module.name)
                        print("Could not find pin ", pinnum ," for ", module.name)
                        break
                    pinslist.append(DUTpin)
                    pinnum+=1
                else: #only runs if successfully ran (will not run on break)
                    term = Terminal(module) #create new terminal
                    term.update(module,pinslist=pinslist)
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
        DUT_Pin_Boxs = [i.b_box for i in self.DUT.shapes if i.layer_name == "pin"]
        xMin=0
        xMax=0
        yMin=0
        yMax=0
        for box in DUT_Pin_Boxs:
            xMin = min(box[1][0],xMin)
            xMax = max(box[0][0],xMax)
            yMin = min(box[1][1],xMin)
            yMax = max(box[0][1],yMax)

        region_max_height = yMax-yMin
        region_max_width = xMax-xMin

        gridSize = self.ws.sch.GetEnv("schSnapSpacing")

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
            #calculate spacing for regions
            while(len(region_sorted) > 0):
                #if(avail_h > .1):
                
                if(box_w <= box_h*ratio):
                    region_sorted = sorted(region_sorted, key=lambda x: x.height, reverse=False)
                   
                else:
                    region_sorted = sorted(region_sorted, key=lambda x: x.width, reverse=False)
                    x = 0
                    y += schematic.ceilByInt(term.height,gridSize) #TODO
                term = region_sorted.pop()

                box_w = schematic.ceilByInt(max(x,box_w),gridSize)
                box_h = schematic.ceilByInt(max(y,box_h),gridSize)
                #x = box_w #TODO
                #avail_h = 
               
                term.plan([x,y])

                x += schematic.ceilByInt(term.width,gridSize)
            region_max_height = max(region_max_height,box_h)
            region_max_width = max(region_max_width,box_w)
        count = 0

        region_max_height = region_max_height + 2
        region_max_width = region_max_width +2 #TODO fix this

        #TODO FIX REGIONS TO USE INFINITE REGIONS IN FORMAT (3x3,4x4,5x5,etc.)
        #only move around planned terminals TODO change back to region as all regions terminals should be planned
        #comment region_removed = [i for i in self.Build if hasattr(i,"planned")]
        rows = round(math.sqrt(max_region))
        height = region_max_height
        width = region_max_width
        #add region sizing
        for region in range(max_region):
            region_sorted = list(filter(lambda x: x.region == region, region_removed))
            x = schematic.ceilByInt((region%rows)*width,gridSize) #TODO
            y = schematic.ceilByInt(math.floor(region/rows)*height,gridSize) #TODO

            for term in region_sorted:
                
                term.position[0] = term.position[0] + x #TODO
                term.position[1] = term.position[1] - y #+ region*3
                count +=1


        #TODO add bounding box type for building

   

    
    #place all terminals in schematic
    def build(self):
        ws= self.ws
        terminals = self.terminals
        logger.info("Start building schematic")
        print("Building!")
        #create cell view for schematic
        #self.view = "schematic_" + self.config.name #TODO standarize this to set in init
        cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "w")
        if(cv is None): #TODO CREATION EXCEPTIONS
            logger.error("Cannot build schematic because schematic not found. Check if open elsewhere")
            print("Error: Schematic not found. Check if open elsewhere")
            return
        self.cv = cv #NOT unnecissary anymore
        
        box = self.DUT.b_box
        [x,y] = schematic.calculateDUTSize(self.DUT)
        [x,y] = [x/2 -2, y/2]
        [x,y] = [schematic.ceilByInt(x,self.gridSize),schematic.ceilByInt(y,self.gridSize)]
        dut_inst = ws.sch.CreateInst( self.cv, self.DUT, "DUT", [x,y], "R0") #place DUT TODO add code to check bounding box
        self.DUTinst = dut_inst
        self.DUTname = dut_inst.name
        #RUN THROGUTH ALL TERMINALS
        for terminal in self.Build: #TODO add check not to load the same master twice
            pin = [p for p in self.DUT.terminals if hasattr(terminal,"label") and p.name == terminal.label]
            if(len(pin)>0):
                dir = self.createWireForFloatingInstPin(dut_inst, pin[0] ,terminal.net)
                #self.ws['CCSCreateWireForFloatingInstPin'](cv,dut_inst, pin[0] ,terminal.label) #TODO make work with no pin heads (also make part of python rather than skill)
            terminal.build(ws,self.cv,dir)

        if(hasattr(self.tconfig, 'scriptpath')): #If custom script is provided, run the script
            ws['load'](self.tconfig.scriptpath)
            ws[self.tconfig.script](self.cv)


        ws.db.Check(self.cv) 
        ws.db.Save(self.cv)
        ws.db.Close(self.cv)
        logger.info("Finished building schematic")
    #end build

    def findDUT(self):
        if(self.cv.instances is not None):
            for inst in self.cv.instances:
                if inst.cell_name == self.DUT.cell_name:
                    self.DUTinst = inst #internal
                    return inst
        return None #none found        

    def createWireStubs(self):
        dut_inst = self.findDUT()
        for terminal in self.DUT.terminals:
            evaluatedPin = [p for p in self.evaluatedPins if hasattr(p,"label") and p.label == terminal.name]
            if(len(evaluatedPin)>0 and hasattr(evaluatedPin[0],"net")):
                #self.createWireForFloatingInstPin(dut_inst, pin[0] ,terminal.net)
                #if  evaluatedPin[0].net =="gnd!":
                #    label = "GND"
                #else:
                label = evaluatedPin[0].label
            else:
                label = terminal.name
            self.createWireForFloatingInstPin(dut_inst, terminal ,label)
    def calculateDUTSize(DUT):
        DUT_Pin_Boxs = [i.b_box for i in DUT.shapes if i.layer_name == "pin"]
        xMin=0
        xMax=0
        yMin=0
        yMax=0
        for box in DUT_Pin_Boxs:
            xMin = min(box[1][0],xMin)
            xMax = max(box[0][0],xMax)
            yMin = min(box[1][1],xMin)
            yMax = max(box[0][1],yMax)

        max_height = yMax-yMin
        max_width = xMax-xMin
        return [max_width,max_height]
    
    def ceilByInt(num, base):
        return base * math.ceil(num/base)
    
    #ported from skill
    def createWireForFloatingInstPin(self,inst,ter,myLabel): #TODO fix issue with no pin wires
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
        self.ws.sch.CreateWireLabel(self.cv , mywire[0], [lab_x,lab_y], myLabel, "upperLeft" ,dir ,"stick" ,0.0625 ,False)
        return [dir,wireDir]
