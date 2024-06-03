from distutils.dir_util import copy_tree
from bs4 import BeautifulSoup
from lxml import objectify, etree

from xml.dom import minidom 
import os

class PlottingTemplate:
    def __init__(self,ws,lib,cell,view) -> None: #for pin terminals
        self.ws = ws
        self.lib = lib
        self.cell = cell
        self.view = view

        pass
    
    #Import ploting template from existing maestro plotting template  
    def import_plotting_template(self, pt_lib, pt_cell, pt_view, pTemplate):
        
        
        #copy the exisitng template
        print(self.ws['getWorkingDir']());
        cellview = self.ws.dd.GetObj(pt_lib,pt_cell,pt_view) #get the cellview for a filelocation on disk
        path = cellview.write_path #get filepath from cellview
        print(path);
        filepath  = path +"/plottingTemplates/"+ pTemplate + "/" + pTemplate+ "_0.cmpt";
        with open(filepath, 'r') as f:
            file = f.read()
        soup = BeautifulSoup(bytes(file, encoding='utf8'),"xml")
        xml_object = objectify.parse(filepath) #get_etree
        
        self.root = objectify.fromstring(bytes(file, encoding='utf8'))
        attrib = self.root.attrib
        #Now that we have the XML we should convert to (remove excess data) a YML/Object format for saving
        self.root
        self.soup = soup

            #get Markers?
            
        print(soup);
        


    #export the loaded template to new maestro cellview
    def export_plotting_template(self,pt_lib,pt_cell,pt_view,pTemplate):
        
        cellview = self.ws.dd.GetObj(pt_lib,pt_cell,pt_view) #get the cellview for a filelocation on disk
        path = cellview.write_path #get filepath from cellview
        #MIN DATA FOR CMPT.group file

        # <?xml version="1.0" encoding="UTF-8" ?>
        # <!--StateFileType saveLoadState-->
        # <topLevel>
        #     <IndexedProp Name="graphFileList">
        #         <SimpleProp Value="Template2_0.cmpt" Type="stringValue" />
        #     </IndexedProp>
        # </topLevel>

        # file = open(filename, 'w',encoding='utf8') 
        # file.write(str(self.soup)) 
        # file.close() 

        filename  = path +"/plottingTemplates/"+ pTemplate + "/" + pTemplate+ "_0.cmpt";
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        #for now just relay the template
        file = open(filename, 'w',encoding='utf8') 
        file.write(str(self.soup)) 
        file.close() 

        etree.tostring(self.root, pretty_print=True)
        self.updateMaestroXML(pt_lib,pt_cell,pt_view,pTemplate)
        
        # root = minidom.Document()
  
        # xml = root.createElement('root')  
        # root.appendChild(xml) 
        
        # productChild = root.createElement('product') 
        # productChild.setAttribute('name', 'Geeks for Geeks') 
        
        # xml.appendChild(productChild) 
        
        # xml_str = root.toprettyxml(indent ="\t")  
        
        # save_path_file = "gfg.xml"

    def updateMaestroXML(self,pt_lib,pt_cell,pt_view,pTemplate):
        cellview = self.ws.dd.GetObj(pt_lib,pt_cell,pt_view) #get the cellview for a filelocation on disk
        path = cellview.write_path #get filepath from cellview
        filepath = path + "/maestro.sdb"
        with open(filepath, 'r') as f:
            file = f.read()

        maestroXML = BeautifulSoup(bytes(file, encoding='utf8'),"xml")
        plottingOptions = maestroXML.find_all("plottingoption")
        #check if plotting templates are an option
        plottingTemplates = [option for option in plottingOptions if "allplottingtemplate" in option.next] #find the plotting templates option

        #TODO check if there isnt a plotting templates already
        if(plottingTemplates is None):
            pass
        plottingTemplates = plottingTemplates[0]
        #plottingTemplates.append("<")

        new_plottingtemplate = maestroXML.new_tag("plottingtemplate")
        #<templatelocation>/orpheus_tests/templatetest1/maestro/plottingTemplates/</templatelocation>
        new_plottingtemplate.string = pTemplate
        location =maestroXML.new_tag("templatelocation")
        templates_filepath  = path +"/plottingTemplates/";
        location.string = templates_filepath
        new_plottingtemplate.append(location)
        plottingTemplates.append(new_plottingtemplate)

        print(maestroXML)
        print(plottingOptions)

        file = open(filepath, 'w') 
        file.write(str(maestroXML)) 
        file.close() 
