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
class config:
    def __init__(self,filename):
        print("reading "+ filename)
        filename = os.path.join(script_dir, "Test_bench_definitions/" + filename)
        with open(filename, 'r') as file:

            self.__dict__.update(json.loads(json.dumps(yaml.safe_load(file)), object_hook=load_object).__dict__)
            print(self.name +" " + self.type +" loaded")#TODO set this to use {} stuff