import os


class UnixOptions:
    @staticmethod
    def add_morpheus_options(parser):
        
        #Add the command option
        parser.add_argument("command",
            nargs='?',
            default=None,
            help="command used by morpheus",
            type=str)
        parser.add_argument("arg1",
            nargs='?',
            help="argument1 used by adddir/removedir",
            type=str)
        #ID for skillbridge
        parser.add_argument(
            "--id",
            metavar="ID",
            default="default",
            help="What the skillbridge ID is (default: default)",
        )

        #Library used for creating new testbenches
        parser.add_argument(
            "--lib",
            metavar="lib",
            default="",
            help="The library used for creating a new testbench",
        )
        parser.add_argument(
            "--config",
            metavar="config",
            default="",
            help="The config file used for creating a new testbench",
        )

        

        #parser.add_argument(
        #    "schematic",
        #    action="store_true",
        #    help="Run schematic creation",
        #)
        #Add the Maestro option
        #parser.add_argument(
        #    "maestro",
        #    action="store_true",
        #    help="Run maestro creation",
        #)

        

        #DUT commands
        parser.add_argument(
            "--DUTlib",
            metavar="DUTLIB",
            default="",
            help="The library that contains the DUT cell in cadence"
        )

        parser.add_argument(
            "--DUTcell",
            metavar="DUTCell",
            default="",
            help="The cell for the DUT in cadence.",
            type=str
        )


        #run without GUI (temp)
        parser.add_argument(
            "--nograph",
            action="store_true",
            help="Run without GUI (default: FALSE)",
            
        )
        #parser.add_argument(
        #    "--adddir",
        #    metavar="ADDDIR",
        #    default=None,
        #    help="Directory to append to search tree in user yml",
        #)
        #parser.add_argument(
        #    "--removedir",
        #    metavar="REMOVEDIR",
        #    default=None,
        #    help="Directory to remove from search tree in user yml",
        #)


    @staticmethod
    def add_schematic_options(parser):
        parser.add_argument('--cell', default='', help='Cell argument')
        parser.add_argument('--lib', default='', help='Lib argument')
        parser.add_argument('--id', default=os.getenv("USER"), help='ID argument')
