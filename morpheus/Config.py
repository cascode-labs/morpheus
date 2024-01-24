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


class config:
    path_locations = list()
    userConfig = None
    types = dict()
    def __init__(self,configName=None,file_type=None):
        if(configName == None):
            return
        if(len(config.path_locations) == 0):
            config.getPaths()
        filename = configName + "." + config_dict_types[file_type] + ".yml" #create filename

        print("Finding "+ filename)
        for path in config.path_locations:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == filename:
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r') as file:
                                #data = yaml.safe_load(file) #cleaner solution?
                                yaml_load = yaml.load(file,Loader=SafeLoaderIgnoreUnknown)
                                json_load = json.loads(json.dumps(yaml_load), object_hook=load_object).__dict__
                                self.__dict__.update(json_load)
                                #if config_dict_types[self.type] != file_type:
                                #    continue
                                print(f"{self.name} {self.type} loaded from {filepath}")
                                self.success = True
                                return
                        except Exception as e:
                            print(f"Error loading {filename}: {e}")
        print("Could not find "+ filename + " in paths");
        self.success = False;
        raise FileNotFoundError
        #except:
        #    print("failed to load")
    def parseType(input):
        config_types[input];
        
        return type;    
    
    def getPaths():
        user_home = os.path.expanduser('~')
        morpheus_home =  os.path.join(user_home,".morpheus")
        
        config.path_locations.append(os.path.join(script_dir, "Test_bench_definitions"))
        config.path_locations.append(morpheus_home)

        config.loadUserConfig() #load user.yml file if not already loaded

            
        if(config.userConfig.success):
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

        config.userConfig.success = False #add that not successful after saving new user config

    def saveUserConfig():
        user_home = os.path.expanduser('~')
        morpheus_home =  os.path.join(user_home,".morpheus")
        
        filename = os.path.join(morpheus_home,"user.sysm.yml");

        with open(filename, 'w') as outfile:
            yaml.dump(config.userConfig, outfile, default_flow_style=False)

    def addDir(dir):
        config.loadUserConfig();
        if(config.userConfig.success):
            config.userConfig.paths.append(dir);
            config.saveUserConfig();
        else:
            print("Failed to find load user.yml, unable to add dir\n");

    def getConfigs(file_type): #TODO test as MIGHT BE BROKEN
        configs = list()
        
        for path in config.path_locations:
            logger.debug(f"Checking {path} for ",config_dict_types[file_type]);
            print(f"Checking {path} for ",config_dict_types[file_type])
            for root, dirs, files in os.walk(path):
                for file in files:
                    print("found file ", file)
                    if(os.path.splitext(file)[1] == ".yml" ):
                        filepath = os.path.join(root, file)
                        
                        try:
                            value = os.path.splitext(os.path.splitext(file)[0])
                            file_name_part = value[0]
                            file_type_part = value[1]
                            if( file_type_part == "." + config_dict_types[file_type]):
                                with open(filepath, 'r') as file:
                                    config_temp = config()
                                    #data = yaml.safe_load(file) #cleaner solution?
                                    config_temp.__dict__.update(json.loads(json.dumps(yaml.load(file,Loader=SafeLoaderIgnoreUnknown)), object_hook=load_object).__dict__)
                                    config_temp.filename = file_name_part
                                    configs.append(config_temp);
                        except Exception as e:
                            print(f"Error loading {filepath}: {e}")
        return configs
    
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None 

SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)

#path_locations = list(os.path.join(script_dir, "Test_bench_definitions"), os.path.join(morpheus_home,"testbenches"))
