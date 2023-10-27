def __add_options(parser):
    """
    Add the `Schematic` options
    """
    parser.add_argument("command", nargs='?',type=str)
    parser.add_argument(
        "--id",
        metavar="ID",
        default="default",
        help="What the skillbridge id is (default: default)",
    )
    #run without GUI (temp)
    parser.add_argument(
        "--nograph",
        action="store_true",
        help="Run without GUI (default: FALSE)",
    )
