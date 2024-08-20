from enum import Enum
import logging
import yaml
import os
from yaml.loader import UnsafeLoader
import types
import json
import sys
if getattr(sys, 'frozen', False): #EXE 
    script_dir = os.path.dirname(sys.executable)
elif __file__: #AS PYTHON CODE
    script_dir = os.path.dirname(__file__)

logger = logging.getLogger(__name__)




def load_object(dct):
    return types.SimpleNamespace(**dct)

class obj(object):
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(k, (list, tuple)):
                setattr(self, k, [obj(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, obj(v) if isinstance(v, dict) else v)
class config_types(Enum):
    TERMINAL = 1
    SCHEMATIC = 2
    TEST = 3
    SYSTEM = 4


config_dict_types = {
    config_types.TERMINAL: "term",
    config_types.SCHEMATIC: "schem",
    config_types.TEST: "test",
    config_types.SYSTEM: "sysm"
}


class config:   #yaml_tag = u"!Nokia" https://stackoverflow.com/questions/64587958/yaml-constructor-constructorerror-while-constructing-a-python-object-cannot-fin
    path_locations = list()
    userConfig = None
    types = dict()
    def __init__(self,configName=None,file_type=None,filepath=None):
        if(filepath is not None):
            self.loadFile(filepath)
            return
        if(configName == None):
            return
        if(len(config.path_locations) == 0):
            config.getPaths()
        filename = configName + "." + config_dict_types[file_type] + ".yml" #create filename

        matching_files = config.searchFiles(name=configName,file_type=file_type)
        if(len(matching_files) > 1):
            print("WARNING MULTIPLE FILES FOUND USING", matching_files[0])
        self.loadFile(matching_files[0]) 
    
    def getPaths():
        user_home = os.path.expanduser('~')
        morpheus_home =  os.path.join(user_home,".morpheus")
        config.path_locations.append(os.path.join(script_dir, "Test_bench_definitions"))
        config.path_locations.append(morpheus_home)
        config.loadUserConfig() #load user.yml file if not already loaded

        #if(config.userConfig is not None):
        for path in config.userConfig.paths: #add all user's paths to path locations
                config.path_locations.append(path)

    def loadUserConfig():
        #TODO add check if success? reduce loads from file
        user_home = os.path.expanduser('~')
        morpheus_home =  os.path.join(user_home,".morpheus")
        try:
            config.userConfig = config("user",config_types.SYSTEM)
        except FileNotFoundError:
            #TODO create new config file for user
            config.createUserConfig()

            pass
    def createUserConfig():
        print("Creating user.sysm.yml!")
        config.userConfig = config()
        #add all default values
        config.userConfig.name= "user config"
        config.userConfig.type= "system"
        config.userConfig.paths = list()
        config.saveUserConfig() #save!

    def saveUserConfig():
        user_home = os.path.expanduser('~')
        morpheus_home =  os.path.join(user_home,".morpheus")
        
        filename = os.path.join(morpheus_home,"user.sysm.yml");
        os.makedirs(os.path.dirname(filename), exist_ok=True) #create morpheus directory if not already
        with open(filename, 'w') as outfile:
            yaml.dump(config.userConfig, outfile, default_flow_style=False)#,transform=strip_python_tags)

    def addDir(dir):
        config.loadUserConfig();
        if(config.userConfig.success):
            config.userConfig.paths.append(dir);
            config.saveUserConfig();
        else:
            print("Failed to find load user.yml, unable to add dir\n");

    def searchFiles(name=None,filename = None, file_type = None):
        matching_files = list()
        file_type =  config_dict_types[file_type]
        if(filename is not None):
            print("Finding "+ filename)
        elif(name is not None):#TODO CHECK FILETYPE
            filename = name + "." + file_type + ".yml" #create filename
            print("Finding "+ filename)
        else:
            print("Finding configs of type" + file_type)

        for path in config.path_locations: #search locations 
            for root, dirs, files in os.walk(path): #into subfolders
                for file in files: #check all files
                    #check filetype
                    value = os.path.splitext(os.path.splitext(file)[0])
                    file_name_part = value[0]
                    file_type_part = value[1][1:] #remove leading dot "."
                    if(file_type_part == file_type):
                        if(filename ==None or filename == file):#only checking for filetype or filename matches
                            filepath = os.path.join(root, file)
                            matching_files.append(filepath)
        if len(matching_files) ==0:
            print("Could not find file")
            raise FileNotFoundError

        return matching_files

    def loadFile(self,filepath):
        with open(filepath, 'r') as file:
            yaml_load = yaml.load(file,Loader=SafeLoaderIgnoreUnknown)
            json_load = json.loads(json.dumps(yaml_load), object_hook=load_object).__dict__
            self.__dict__.update(json_load)
            value = os.path.splitext(os.path.splitext(filepath)[0])
            file_type_part = value[1][1:] #remove leading dot "."
            print(f"{self.name} {file_type_part} loaded from {filepath}")

    def updateInstance(self,OBJ):
        for key in self.__dict__: #GO RECURSIVELY EVENTUALLY
            defintion = self.__dict__[key]
            if(isinstance(defintion, str)):
                #https://stackoverflow.com/questions/28094590/ignore-str-formatfoo-if-key-doesnt-exist-in-foo
                #s = Template(defintion).safe_substitute(**self.global_dict)
                self.__dict__[key] = defintion.format_map(OBJ.global_dict) #update config file dict with globals
        OBJ.__dict__.update(self.__dict__)
        
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None 

SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)

#path_locations = list(os.path.join(script_dir, "Test_bench_definitions"), os.path.join(morpheus_home,"testbenches"))
def strip_python_tags(s):
    result = []
    for line in s.splitlines():
        idx = line.find("!!python/")
        if idx > -1:
            line = line[:idx]
        result.append(line)
    return '\n'.join(result)