import argparse
try:
    from . import toml_parser
except ImportError:
    import toml_parser


# NOT YET IMPLEMENTED


def parse(prog_name: str):
    """
    parse user arguments from STDIN.
    """
    parser = argparse.ArgumentParser(
        usage=f'{prog_name} [options] -t[--toml-file] SERVERLIST')
    parser.add_argument("--print-table", "-s", default=False,
                        action="store_true",
                        help='''
                        output the final table connection to stdout.
                        ''')
    parser.add_argument("--verbose", "-v",
                        default=False,
                        action="store_true",
                        help="prints a log at runtime")
    parser.add_argument("--output-log", "-o",
                        default=False,
                        nargs=1,
                        help="outputs a log to the current directory, as a filename")
    parser.add_argument("--new", "-n",
                        default=False,
                        nargs=1,
                        help="""
                        creates a new toml file in the
                        current working directory.
                        """)
    parser.add_argument("--toml-file", "-t",
                        nargs="?",
                        type=str,
                        help='''
                        Toml file to get parsed. If none specified, use default
                        ''',
                        default=toml_parser.get_toml_path())
    parser.add_argument("--timeout", "-T", default=4,
                        nargs="?",
                        type=int,
                        help="Set the timeout (in seconds)")
    parser.add_argument("--version", "-V", default=False,
                        action="store_true",
                        help="print the version")
    return parser.parse_args()


if __name__ == "__main__":
    parse("sat")
