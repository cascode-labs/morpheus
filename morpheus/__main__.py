import argparse
import multiprocessing
import pwd
from time import sleep
from skillbridge import Workspace
from morpheus.CadenceManager import cadenceManager

import signal
import sys



#from morpheus import UnixOptions
from morpheus.GUIController import *
from morpheus.Schematic import *


import os

from collections import defaultdict

from morpheus.UnixOptions import UnixOptions
from morpheus.UnixCommands import UnixCommands

from morpheus import morpheus_home

frozen = 'not'
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    frozen = 'ever so'
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Get the directory of the script or executable
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

#borrowed and modified from pyinstaller
logger = logging.getLogger(__name__)


# This is used by the ``--debug`` option.
class _SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            # The underlying implementation of ``RawTextHelpFormatter._split_lines`` invokes this; mimic it.
            return text[2:].splitlines()
        else:
            # Invoke the usual formatter.
            return super()._split_lines(text, width)
def __add_options(parser):
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
        help='Show program version info and exit.',
    )
class _MorphArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self._morph_action_groups = defaultdict(list)
        super().__init__(*args, **kwargs)

    def _add_options(self, __add_options: callable, name: str = ""):
        """
        Mutate self with the given callable, storing any new actions added in a named group
        """
        n_actions_before = len(getattr(self, "_actions", []))
        __add_options(self)  # preserves old behavior
        new_actions = getattr(self, "_actions", [])[n_actions_before:]
        self._morph_action_groups[name].extend(new_actions)

    def _option_name(self, action):
        """
        Get the option name(s) associated with an action

        For options that define both short and long names, this function will
        return the long names joined by "/"
        """
        longnames = [name for name in action.option_strings if name.startswith("--")]
        if longnames:
            name = "/".join(longnames)
        else:
            name = action.option_strings[0]
        return name

    def _forbid_options(self, args: argparse.Namespace, group: str, errmsg: str = ""):
        """Forbid options from a named action group"""
        options = defaultdict(str)
        for action in self._pyi_action_groups[group]:
            dest = action.dest
            name = self._option_name(action)
            if getattr(args, dest) is not self.get_default(dest):
                if dest in options:
                    options[dest] += "/"
                options[dest] += name

        # if any options from the forbidden group are not the default values,
        # the user must have passed them in, so issue an error report
        if options:
            sep = "\n  "
            bad = sep.join(options.values())
            if errmsg:
                errmsg = "\n" + errmsg
            raise SystemExit(f"option(s) not allowed:{sep}{bad}{errmsg}")


def generate_parser() -> _MorphArgumentParser:
    """
    Build an argparse parser for morpheus's main CLI.
    """

    parser = _MorphArgumentParser(formatter_class=_SmartFormatter)
    parser.prog = "morpheus"
    #subparsers = parser.add_subparsers(dest='command')

    UnixOptions.add_morpheus_options(parser)
    #schematic_parser = subparsers.add_parser('schematic')
    #UnixOptions.add_schematic_options(schematic_parser)




    return parser

#https://stackoverflow.com/questions/842059/is-there-a-portable-way-to-get-the-current-username-in-python
def get_username():
    return pwd.getpwuid(os.getuid())[0]



global_ws = None
def main(morph_args: list | None = None):


#setup logger
    logging_file_location =  os.path.join(morpheus_home,'morpheus.log')
    logging.basicConfig(filename=logging_file_location, level=logging.DEBUG) #TODO change logging settings via unix command
#port to STDOUT
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f'Logging Started at {logging_file_location}')

    #old parser code
    parser = argparse.ArgumentParser(
                    prog='Morpheus',
                    description='Testbench Generator',
                    epilog='Run --help for options (not ready yet!)')
    parser.add_argument('-c', '--cell')
    parser.add_argument('-l', '--lib')
    #parser.add_argument('-i', '--id')

    #args = parser.parse_args()



    #new parser code
    parser = generate_parser()
    if morph_args is None:
            morph_args = sys.argv[1:]
    try:
        index = morph_args.index("--")
    except ValueError:
        index = len(morph_args)
    
    args = parser.parse_args(morph_args[:index])
    
    logger.info(f"Command is {args.command}")
    try: #try catch should not be needed because of default values
        cell= args.cell
    except:
        cell = ""
    try:
        lib = args.lib
    except:
        lib = ""
        
    id = args.id
    if(id == "default"):
        path = os.getcwd() 
        username = get_username()
        id = f"{username}@{path}"
        id = id.replace("/","")
        id = id.replace("\\","")
        print(f"the autogenerated id is {id}")
      
    #TODO try id and select new ID if already used
    #create cadence instance
    manager = None
    try:
        logger.info(f'Attempting to connect to SkillBridge with ID {id}')
        ws = Workspace.open(id) #create ws in main rather than in GUI or elsewhere
        ws["print"]("Hello World! Morpheus has started!\n")
        
    except:
        #cadence_process = multiprocessing.Process(target=start_cadence_manager, args=(id,))
        #cadence_process.start()

        manager = cadenceManager(id) #TODO add unix option for precommand
        attempts = 0

        while attempts < 10: #Use other form of checking server other than a failure
            try:
                ws = Workspace.open(id)
                ws["print"]("Hello World! Morpheus has started!")
                break;
            except: #id is not ready yet wait 5 seconds
                sleep(1)
                attempts += 1
        #if failed try to kill server/virtuoso
        
    try:
        UnixCommands(ws,args)

        
        if not args.nograph and not args.command: #only run gui if no command set
            
            logger.info('Starting GUI')
            config.getPaths()#Get paths for tests
            Controller = GUIController(ws)
            Controller.startGUI()
    except Exception as e:
        logger.info("Error in execution closing morpheus");
        logger.info(e)
    
    #TODO move to before the unix options and GUI 
    if(manager is not None): #we created a cadence instance! Keep it going with 5 minute timeout
        pid = os.fork() 
        if pid == 0 : 
            manager.loop()
        else:
            logger.info("Thanks for using Morpheus! Cadence with Skillbridge will be running in the background until timeout!")
            os._exit(os.EX_OK)






main()



