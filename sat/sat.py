#!/usr/bin/env python
import sys
import os
"""
This file is our initialization file for the entire project.
"""
name = "sat"
desc = "Checks accessibility of pre-defined servers"
__version__ = "1.0"
__author__ = "Jonathan Villanueva (westwardfishdme)"


def start():
    """
    tries to import the main file, catches any importing
    issues of the main libraries prior to running the code.

    Most errors are caught within our main file, however-- any other
    exception is handled within this file.
    """
    try:
        from .modules import main
        from .modules import arguments as args
    except ImportError:
        from modules import main
        from modules import arguments as args

    try:
        # main.check_priv()  # the error is handled within the file already...
        main.run(name, __version__)
    except Exception as e:
        print(f"[ ERROR ] {name} {__version__} ran into a fatal error!:\n"
              f"{type(e).__name__}{e.__traceback__}{e}", file=sys.stderr)


if __name__ == "__main__":
    try:
        start()
    except EOFError:
        exit(0)
    except KeyboardInterrupt:
        exit(0)
