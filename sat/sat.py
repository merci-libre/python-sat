#!/usr/bin/env python
import sys
import traceback
"""
This file is our initialization file for the entire project.
"""
name = "sat"
desc = "Checks accessibility of pre-defined servers"
__version__ = "1.2"
__author__ = "Jonathan Villanueva (westwardfishdme)"


def start():
    """
    tries to import the main file, catches any importing
    issues of the main libraries prior to running the code.

    Most errors are caught within our main file, however-- any other
    exception is handled within this file.
    """
    # try to import these libraries
    try:
        from serveradmintool.modules import main
        from serveradmintool.modules import ansi
    except ImportError:
        from .modules import main
        from .modules import ansi

    try:
        # main.check_priv()  # the error is handled within the file already...
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
    start()  # start our program
