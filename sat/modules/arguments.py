import argparse
import sys

argument_values = {}


# NOT YET IMPLEMENTED
def parse(prog_name: str):
    parser = argparse.ArgumentParser(usage=f'{prog_name} [options]')
    parser.add_argument("--print-table", "-s", nargs=None,
                        default=True)
    parser.add_argument("--print-log", "-L", nargs=None, default=False)
    parser.add_argument("--output-log", "-o", default=True)
    parser.print_help()
    print("\n[note]: arguments not yet implemented")
