#!/usr/bin/env python3
import sys
"""
This file is our initialization file for the entire project.
"""
import traceback
name = "sat"
desc = "Checks accessibility of pre-defined servers"
__version__ = "2.0p1"
__author__ = "Jonathan Villanueva (westwardfishdme)"


def start():
    """
    Tries to import the main file, catches any importing
    issues of the main libraries prior to running the code.

    Most errors are caught within our main file, however-- any other
    exception is handled within this file.

    This breaks traditional naming conventions used in class
    to not get confused with the library file. Since the library's
    main file is called "main" to refer to our main.py file inside
    of the installed library, I titled this function start instead.
    """
    # try to import these libraries
    try:
        from sat.modules import main
        from sat.modules import ansi
    except ImportError:
        from modules import main
        from modules import ansi
    except ModuleNotFoundError:
        from .modules import main
        from .modules import ansi

    try:
        main.run(name, __version__)
    except KeyboardInterrupt:
        print("\n\nExiting the script...", file=sys.stderr)
        exit(0)
    except EOFError:
        print("\n\nExiting the script...", file=sys.stderr)
        exit(0)
    except Exception as e:
        print(f"[{ansi.RED} ERROR {ansi.END}] {name} {__version__} ran into a fatal error!:\n"
              f"\n{type(e).__name__}:{ansi.RED} {e}{ansi.END}\n\n{
              traceback.format_exc(6)}", file=sys.stderr)
        print("Report this issue to the developer on github", file=sys.stderr)


if __name__ == "__main__":
    """
    This is the correct invocation of main
    as described by
    https://docs.python.org/3/library/__main__.html

    We also may allow the user to install this package
    with the VENV's pip at a later date.
    """
    start()  # start our program
