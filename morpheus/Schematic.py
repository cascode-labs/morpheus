from morpheus.Config import *
import re
import copy
import math
import logging
#from morpheus.Exceptions.SelectionBox import SelectionBoxException

from morpheus.MorpheusObject import morpheusObject
from morpheus.MorpheusDict import morpheusDict


properties_to_remove =[
    "ws", "session", "asi_session", #change based on cadence session
    "global_dict","cv",
    "equationDict", #TODO REMOVE not needed anymore
    "config" #TDOD remove not needed anymore
]

from morpheus.Instance import instance
logger = logging.getLogger("morpheus")

class box:
    def __init__(self,w,h) -> None:
        self.w =w
        self.h =h
        pass
class regionClass:
    def __init__(self,instances=list()) -> None:
        self.instances =instances
        pass

#CONFIG view for schematic (TODO should be part of scheamtic)
class schematicConfig(morpheusObject):
    def __init__(self,ws,config,lib="", global_dict = dict()) -> None:
        pass
    def createConfig(self,Config):
        config_view = self.ws.hdb.Open(self.lib, self.cell, "config_" + Config.name, "a", "CDBA")
        self.ws.hdb.SetTopCellViewName(config_view, self.lib, self.cell, Config.schematic)
        self.ws.hdb.SetDefaultLibListString(config_view, "myLib")
        self.ws.hdb.SetDefaultViewListString(config_view, "spectre schematic veriloga")
        self.ws.hdb.SetDefaultStopListString(config_view, "spectre")
        self.ws.hdb.Save(config_view)
        self.ws.hdb.Close(config_view)



class schematic(morpheusObject):

    def __init__(self,ws,config,lib="", global_dict = dict()) -> None:

        self.lib =lib
        self.ws = ws
        self.config = config
        
        #DEFAULTS
        self.cell = "Morpheus_Testbench"
        self.view = "schematic"
        self.region_padding = 1
        self.subregion_padding = 0.2
        self.terminals = dict()
        self.instances = dict()#TODO remame
        self.gridSize = self.ws.sch.GetEnv("schSnapSpacing") #used for snapping everything to grid
        
        #load config view
        self.global_dict = morpheusDict(global_dict)
        config.updateInstance(self)

        
        #check if view already exists
        cvid = self.ws.dd.GetObj(self.lib,self.cell,self.view) #delete

        self.evaluate()#always evaluate 
        if(cvid is None):
            #just build?
            pass
        else:
            self.cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "a") #appendmode. DONT DELETE WORK
            #self.findDUT()#potential break if no DUT TODO fix
            ws.db.Close(self.cv)
            #check if open and give warning if so
    

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
        #ALWAYS RESET TO CONFIG?
        self.config.updateInstance(self)
            #https://stackoverflow.com/questions/4081217/how-to-modify-list-entries-during-for-loop
        self.instances[:] = [instance(self.ws,inst,self.global_dict) for inst in self.instances]

        if(hasattr(self.config,"dictionary_variables")): #TODO confirm all variables needed are provided
            pass
        #match pin names to terminals defined in the PLAN section of schematic config
        #for(term in self.config.Build):
        logger.info("Starting evaulation for DUT pins")
        #evaluation
        for inst in self.instances:
            inst.evaluate()
            self.global_dict.update({inst.name:inst})#append to global dictionary TODO local dictionary instead?
        
        #Convert list into dictionary
        instances = self.instances
        self.instances = dict()
        for inst in instances:
            self.instances.update({inst.name : inst})
        logger.info("Evaluated all Instances")


    def plan(self): #USED TO CALCULATE LOCATIONS OF TERMINALS IN PLAN TODO just pass the gridsize?
        planned_insts = list()
        #move all terminals to schematic
        for key, inst in self.instances.items():
            planned_insts.append(inst)
            planned_insts.extend(inst.terminals) #add all instances to schematic
        
        non_region_removed = [i for i in planned_insts if hasattr(i,"region")] #only terminals that have regions
        #still needed for NOCONNECT
        
        max_region = 9
        self.regions = list()
        regions_temp = list()
        region_sorted_list = list()
        #sort by Region
        for region_num in range(max_region):
            region_sorted = list(filter(lambda x: x.region == region_num, non_region_removed))
            if len(region_sorted) > 0:
                region_sorted_list.append(region_sorted)
                new_region = regionClass(region_sorted) #blank for now
                #s#elf.regions.append(new_region)
                regions_temp.append(new_region)
        #sort by type
        new_regions = list()
        for region in regions_temp: #REGION
            types = schematic.unique(region.instances,"type")
            
            new_region = regionClass()
            new_regions.append(new_region)
            #type_region = regionClass(types)
            subregions = list()
            for sch_type in types:#SUBREGION
                types_sorted = list(filter(lambda x: x.type == sch_type.type, region.instances))

                for inst in types_sorted: #INST
                    inst.plan()
                [typeregion_w,typeregion_h] = self.layout(types_sorted)
                
                subregion = regionClass(types_sorted[:])
                subregion.width = typeregion_w  #+ self.subregion_padding*2
                subregion.height = typeregion_h #+ self.subregion_padding*2
                subregions.append(copy.copy(subregion))
            new_region.instances = subregions[:]
            self.cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "w")
            [region_w,region_h] = self.layout(new_region.instances)
            #new_region = regionClass(types_sorted)
            #new_region.instances.append(type_region)
            new_region.width =region_w + self.region_padding
            new_region.height = region_h + self.region_padding
            
            self.regions.append(copy.copy(new_region))
            #new_region.reset() 
        [total_width,total_height] = self.layout(self.regions)

        #plan


    #https://stackoverflow.com/questions/26043482/how-to-get-unique-values-from-a-python-list-of-objects modified slightly
    def unique(list1,parameter):
        # intilize a null list
        unique_list = []
        parameter_list = []
        # traverse for all elements
        for x in list1:
            param_val =getattr(x,parameter)
            # check if exists in unique_list or not
            if param_val not in parameter_list:
                parameter_list.append(param_val)
                unique_list.append(x)

        return unique_list
   

    def layout(self,boxes):#TODO ADD padding
        layout_w = 0
        layout_h = 0
        ratio = 5
        x = 0
        y = 0
        
        self.cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "w")
        regionbox = self.ws.sch.CreateNoteShape( self.cv, "rectangle", "dashed", [ [0, 0],[1,1]] )
        while(len(boxes) > 0):
            if(layout_w <= layout_h*ratio):
                boxes = sorted(boxes, key=lambda x: x.height, reverse=False) #sort by heights
                box = boxes.pop()
                box.x =x #add inst/region x and y
                layout_w = schematic.ceilByInt(max(x+box.width, layout_w),self.gridSize)
                x += schematic.ceilByInt(box.width,self.gridSize)
            else:
                boxes = sorted(boxes, key=lambda x: x.width, reverse=False) # sort by widths
                box = boxes.pop()
                box.x =0 #add inst/region x and y
                x = 0
                x += schematic.ceilByInt(box.width,self.gridSize)
                y += schematic.ceilByInt(layout_h,self.gridSize) #TODO
                #layout_h =box.height + layout_h
            box.y = y

            #self.ws.sch.CreateNoteShape( self.cv, "rectangle", "solid", [ [box.x, box.y],[box.x+box.width,box.y+box.height]] )

            
            layout_h = schematic.ceilByInt(max(box.height+y,layout_h),self.gridSize)
            regionbox.b_box= [[0,0],[layout_w,layout_h]]
            regionbox.b_box= [[0,0],[layout_w,layout_h]]

        return [layout_w,layout_h]
        
    def ceilByInt(num, base):
        return base * math.ceil(num/base)
    #place all terminals in schematic
    def build(self):
        logger.info("Start building schematic")
        self.cv = self.ws.db.OpenCellViewByType(self.lib, self.cell,self.view, "schematic", "w")

        if(self.cv is None): #TODO CREATION EXCEPTIONS
            logger.error("Cannot build schematic because schematic not found. Check if open elsewhere")
            return
        
        for region in self.regions:
            region_x1 = region.x + region.width;
            region_x2 = region.x;
            region_y1 = region.y + region.height;
            region_y2 = region.y;
            self.ws.sch.CreateNoteShape( self.cv, "rectangle", "dashed", [[region_x1,region_y1],[region_x2, region_y2]] )
            for subregion in region.instances:
                x= subregion.x + region.x #+ self.region_padding
                y= subregion.y + region.y #+  self.region_padding
                box_x1 = x #+ subregion.width/2
                box_x2 = x+ subregion.width
                box_y1 = y #+ subregion.height/2
                box_y2 = y+ subregion.height
                self.ws.sch.CreateNoteShape( self.cv, "rectangle", "solid", [ [box_x2, box_y2],[box_x1,box_y1]] )
                for inst in subregion.instances:
                   inst.build(self.cv,0,x,y,self.gridSize)

        self.ws.db.Check(self.cv) 
        self.ws.db.Save(self.cv)
        self.ws.db.Close(self.cv)
        logger.info("Finished building schematic")
    #end build

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
