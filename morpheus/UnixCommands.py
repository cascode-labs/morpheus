from morpheus import Config
from morpheus.Config import *
from morpheus.Maestro import maestro
from morpheus.Schematic import schematic


def UnixCommands(ws,args):

    #--adddir command 
    if(args.command == "adddir"):
        config.addDir(args.arg1)

    if(args.command == "adddir"):
        config.removeDir(args.arg1)
    
    #schematic - creates a testbench schematic for user
    if(args.command == "schematic"):
        #add check for all required args
        tconfig = None
        DUT = ws.db.open_cell_view(args.DUTlib,args.DUTcell,"symbol")
        configFile = Config.config(args.config,Config.config_types.SCHEMATIC)
        Testbench = schematic(ws,args.lib,DUT,configFile, tconfig)
        Testbench.evaluate();
        Testbench.plan();
        Testbench.build();
    
    if(args.command == "maestro"):
        tconfig = None
        DUT = ws.db.open_cell_view(args.DUTlib,args.DUTcell,"symbol")
        configFile = Config.config(args.config,Config.config_types.TEST)
        Testbench = maestro(ws,args.lib,DUT,test = configFile)