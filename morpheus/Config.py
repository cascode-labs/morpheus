from enum import Enum
import yaml
import os
from yaml.loader import UnsafeLoader
import types
import json
script_dir = os.path.dirname(__file__)

import os, sys

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
    os.chdir(script_dir)


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
    "terminal": config_types.TERMINAL,
    "schematic": config_types.SCHEMATIC,
    "test": config_types.TEST,
    "system": config_types.SYSTEM
}


class config:
    path_locations = list()
    userConfig = None
    types = dict()
    def __init__(self,filename=None,file_type=None):
        if(filename == None):
            return
        if(len(config.path_locations) == 0):
            config.getPaths()
        #filename = os.path.join(script_dir, "Test_bench_definitions/" + filename)
        #try
        print("Finding "+ filename)
        for path in config.path_locations:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == filename:
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r') as file:
                                #data = yaml.safe_load(file) #cleaner solution?
                                self.__dict__.update(json.loads(json.dumps(yaml.safe_load(file)), object_hook=load_object).__dict__)
                                if config_dict_types[self.type] != file_type:
                                    continue
                                print(f"{self.name} {self.type} loaded from {filepath}")
                                self.success = True
                                return
                        except Exception as e:
                            print(f"Error loading {filename}: {e}")
        print("Could not find "+ filename + " in paths");
        self.success = False;
        #except:
        #    print("failed to load")
    def parseType(input):
        config_types[input];
        
        return type;    
    
    def getPaths():
        script_dir = os.path.dirname(__file__)
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
            config.userConfig = config("user.yml",config_types.SYSTEM)
        except FileNotFoundError:
            #TODO create new config file for user
            pass
    
    def saveUserConfig():
        user_home = os.path.expanduser('~')
        morpheus_home =  os.path.join(user_home,".morpheus")
        
        filename = os.path.join(morpheus_home,"user.yml");

        with open(filename, 'w') as outfile:
            yaml.dump(config.userConfig, outfile, default_flow_style=False)

    def addDir(dir):
        config.loadUserConfig();
        if(config.userConfig.success):
            config.userConfig.paths.append(dir);
            config.saveUserConfig();
        else:
            print("Failed to find load user.yml, unable to add dir\n");

    def getConfigs(file_type):
        configs = list()
        
        for path in config.path_locations:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if(os.path.splitext(file)[1] == ".yml" ):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r') as file:
                                config_temp = config()
                                #data = yaml.safe_load(file) #cleaner solution?
                                config_temp.__dict__.update(json.loads(json.dumps(yaml.safe_load(file)), object_hook=load_object).__dict__)
                                if config_dict_types[config_temp.type] != file_type:
                                    continue
                                configs.append(config_temp);
                        except Exception as e:
                            print(f"Error loading {filepath}: {e}")
        return configs
    

#path_locations = list(os.path.join(script_dir, "Test_bench_definitions"), os.path.join(morpheus_home,"testbenches"))
