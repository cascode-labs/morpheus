import argparse
from morpheus.GUIController import *


import os
def main():
    parser = argparse.ArgumentParser(
                    prog='Morpheus',
                    description='Testbench Generator',
                    epilog='Run --help for options (not ready yet!)')
    parser.add_argument('-c', '--cell')
    parser.add_argument('-l', '--lib')
    parser.add_argument('-i', '--id')

    args = parser.parse_args()
    try:
        cell= args.cell
    except:
        cell = ""
    try:
        lib = args.lib
    except:
        lib = ""
    
    id = args.id
    if not id:
        id = os.getenv("USER")
    
    


    Controller = GUIController(id)
    Controller.startGUI()
main()