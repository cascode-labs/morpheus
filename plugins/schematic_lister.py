# import sys
# import importlib.util

# file_path = 'pluginX.py'
# module_name = 'pluginX'

# spec = importlib.util.spec_from_file_location(module_name, file_path)
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)

# # Verify contents of the module:
# print(dir(module))
#https://stackoverflow.com/questions/301134/how-can-i-import-a-module-dynamically-given-its-name-as-string

#https://stackoverflow.com/questions/9865455/adding-functions-from-other-files-to-a-python-class
from morpheus.Schematic import *

def lister(self):
    for instance in self.instances:
        print(instance.name)
print("PLUGIN!")
method_list = [func for func in dir(schematic) if callable(getattr(schematic, func)) and not func.startswith('__')]
print("schematic methods before")
print(method_list)


schematic.lister = lister

import inspect
method_list = [func for func in dir(schematic) if callable(getattr(schematic, func)) and not func.startswith('__')]

call_method_list = [getattr(schematic, func) for func in dir(schematic) if callable(getattr(schematic, func)) and not func.startswith('__')]
for method in call_method_list:
    if(callable(method)):
    #args,_,_,values = inspect.getargvalues(myframe)
        print(inspect.getfullargspec(method))
    else:
        print(type(method))
print("schematic methods after")
print(method_list)