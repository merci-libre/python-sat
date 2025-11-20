#!/usr/bin/env python
"""
This is our main module, it runs the main program, catches
any missing library modules, fatal errors, and mismatched python versions.
"""

# python venv + standard modules
import os
import time
import threading

# try importing a major depend
# my modules
try:
    from . import connectivity
    from . import tables
    from . import log
    from .errors import eprint
    # we use eprint on its own, but we want to be more
    # verbose in this file with error printing.
    from . import errors
    from . import toml_parser
    from . import arguments
except ImportError:
    raise errors.Main.ImportError


class Output():
    def log(clear=True, initial=False):
        log.print_log(clear, initial)

    def table(initial):
        tables.draw_table(initial)

    def on_join(initial=False, clear=True, verbose=False):
        tables.draw_table(initial)
        if initial:
            clear = False
        if verbose:
            log.print_log(clear, initial)


def __check_values(args, server, ip, ports, scan) -> int:
    """
    returns a signal code telling the program how to handle the error
    0's means nothing is wrong.
    1's just skip the thread loop
    2's handles port scanning.
    """
    check = errors.Check()
    SIGNAL = 0

    log.notify(f"[Main]: checking values...")
    try:
        ip = check.ip(ip, server)
        log.write(f"[Main]: IP address for {server} is valid.")
        ports = check.ports(ports, server)
        log.write(f"[Main]: port(s) for {server} is valid")
        scan = check.scan(scan, server)
        log.write(f"[Main]: scan value for {server} is valid")
        SIGNAL = 0
    except errors.ConnectivityDefinitions.IPAddressErrors.IncorrectType:
        log.error(f"{server} IP address is the wrong data type!")
        SIGNAL = 1
    except errors.ConnectivityDefinitions.IPAddressErrors.BadIPAddressValue:
        log.error(f"{server} has no IP address!, SKIPPING")
        SIGNAL = 1
    except errors.ConnectivityDefinitions.Ports.PortOutOfRange:
        log.error(
            f"{server} contained port value outside"
            "of the range (1, 65535)")
        SIGNAL = 2
    except errors.ConnectivityDefinitions.Ports.IncorrectType:
        log.error(
            f"{server} had a port address with an incorrect type\n",
            f"ports={ports}")
        SIGNAL = 2
    except errors.ConnectivityDefinitions.Scan.IncorrectType:
        SIGNAL = 2
    if args.verbose:
        Output.log()
    return (SIGNAL, ip, ports, scan)


def __create_threads(args, servers: list, timeout: int) -> list:
    """
    This function creates our main threads.
    It further deserializes the server data provided
    by the toml parser, allowing our program to use
    the data within to load our variables, and load
    the threads.
    """
    server_information = servers.get("servers").items()
    threads = []

    # our data types
    for (server, data) in server_information:
        # Gets the deserialized data from the parsed toml file
        ip = data.get("ip")
        ports = data.get("ports")
        scan = data.get("scan")
        (signal, ip, ports, scan) = __check_values(
            args, server, ip, ports, scan)

        match signal:
            # check the return signals from __check_values()
            case 0:
                pass
            case 1:
                continue
            case 2:
                ports = None
                scan = False

        # ========load the threads======= #
        connectivity.connections[ip] = ["awaiting", None]

        # Update the map tables
        tables.UpdateTables(connectivity.open_ports,
                            connectivity.closed_ports,
                            connectivity.connections)
        try:
            t = threading.Thread(
                target=connectivity.test, args=(ip, ports, scan, timeout))
            t.daemon = True
            log.info(f"Loading thread {t} with values:ip={ip}, Ports={
                     ports} scan={scan},timeout={timeout}")
            # run the thread as a daemon so that we can catch SIGINT
            threads.append(t)
        except Exception:
            raise errors.Threads.FailedToCreate

    if args.verbose:
        Output.log()
    return threads


def __join_threads(threads: list, timeout: int, args):
    """
    connects the threads, with a timeout.
    Default timeout is 18 seconds, however, can be changed with the -T
    argument. e.g:

    (python sat -T 6 == timeout=22)
    ```
    timeout = (timeout*2)+10
    ```

    6 for ping, 6 for http, 12s total testing.
    Before killing, 10 seconds to join.
    """

    timeout = (timeout*2)+10
    for thread in threads:
        thread.join(timeout)
        Output.on_join(verbose=args.verbose)
        log.write(f"[Main Thread]: {thread} joined!")
        log.info(f"[Updated Connections]:{tables.UpdateTables.connections}")
        # draw table
        tables.UpdateTables(connectivity.open_ports,
                            connectivity.closed_ports,
                            connectivity.connections)


def run(name: str, version: str):
    """
    This is our main function, it handles the entire program.
    If an error occurs within here, it returns with a fatal error
    to the program invocation.
    """
    # initialize our arguments and load variables
    date = time.asctime()
    log.start(f"{name} ver. {version} on {date}")
    args = arguments.parse(name)
    servers_tomlfile = args.toml_file
    timeout = args.timeout
    try:
        servers = toml_parser.parse_toml(servers_tomlfile)
    except errors.TomlFiles.TomlFileMissing:
        eprint(f"{servers_tomlfile}.toml does not exist!")
        exit(1)
    except errors.TomlFiles.DeserializationFailure:
        eprint(f"{servers_tomlfile} doesn't look like a toml file...")
        exit(1)

    # set the timeout feature.
    if args.timeout < 2 and not args.timeout == 0:
        eprint("Timeout cannot be shorter than 2 seconds!")
        exit(1)

    # if the user sets the argument to 0, timeout never.
    if args.timeout == 0:
        timeout = 999

    # add messages to the log, and print the table
    if args.version:
        print(f"{name} ver. {version}")
        exit(0)
    if args.new:
        if os.path.exists(args.new[0]):
            eprint(f"{args.new[0]} exists!")
            exit(1)
        toml_parser.write_toml(args.new[0])
        exit(0)
    threads: list = __create_threads(args, servers, timeout)
    # get the servers information from the toml file and parse it
    log.write(f"TOML {servers_tomlfile} loaded!")
    Output.on_join(initial=True, verbose=args.verbose)

    # create threads and draw our initial table after threads.
    del servers_tomlfile, servers

    # start the threads
    for thread in threads:
        log.start(f"{thread}")
        thread.start()

    # handle joining threads
    log.notify("[main] Joining threads...")
    log.info(f"threads to join: {threads.__len__()}")
    __join_threads(threads, timeout, args)

    if args.verbose:
        Output.table(True)

    if args.output_log:
        log.write_log(args.output_log[0])
