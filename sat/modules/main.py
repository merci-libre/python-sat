#!/usr/bin/env python
"""
This is our main module, it runs the main program, catches
any missing library modules, fatal errors, and mismatched python versions.
"""

# python venv + standard modules
import time
import threading

# try importing a major depend
# my modules
try:
    from . import connectivity
    from . import tables
    from . import ansi
    from . import log
    from .errors import eprint
    # we use eprint on its own, but we want to be more
    # verbose in this file with error printing.
    from . import errors
    from . import toml_parser
    from . import arguments
except ImportError:
    raise errors.Main.ImportError


def __check_values(server, ip, ports, scan) -> int:
    """
    returns a signal code telling the program how to handle the error
    0's means nothing is wrong.
    1's just skip the thread loop
    2's handles port scanning.
    """
    check = errors.Check()
    SIGNAL = 0

    try:
        check.ip(ip, server)
        log.write(f"[Main]: IP address for {server} is valid.")
        check.ports(ports, server)
        log.write(f"[Main]: port(s) for {server} is valid")
        check.scan(scan, server)
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
    return SIGNAL


def __create_threads(servers: list, timeout: int) -> list:
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
        # tad bit auto correct, port or ports will work
        ports = data.get("ports")

        if data.keys().__contains__("port"):
            ports = data.get("port")
        scan = data.get("scan")

        match __check_values(server, ip, ports, scan):
            # check the return signals from __check_values()
            case 0:
                pass
            case 1:
                continue
            case 2:
                ports = None
                scan = False

        if type(ports) is list:
            ports = list(dict.fromkeys(ports))
            ports.sort()

        # we actually can just check this one in line
        # load the threads
        connectivity.connections[ip] = ["awaiting", None]
        try:
            t = threading.Thread(
                target=connectivity.test, args=(ip, ports, scan))
            log.notify(f"[Main Thread]: Loading thread {
                t} with values:{ansi.END}\n\tip={ip}\n\tPorts={ports}, scan={scan},timeout={timeout}")
            threads.append(t)
        # this is a rather vague exception, but it catches the issue as a catch all.
        except Exception:
            raise errors.Threads.FailedToCreate
    return threads


def __join_threads(threads: list, timeout: int):
    """
    connects the threads, with a timeout.
    Default timeout is 10 seconds, however, can be changed with the -T
    argument. e.g:

    (python sat -T 6 == timeout=13)
    ```
    timeout = (timeout*2)+1
    ```

    6 for ping, 6 for http, 12s total testing.
    Before killing, 1 second to join.
    """

    timeout = (timeout*2)+1
    for thread in threads:
        log.notify(f"[Values]:\n{connectivity.connections}")
        thread.join(timeout)
        log.write(f"[Main Thread]: {thread} joined!")
        tables.UpdateMaps(connectivity.open_ports, connectivity.closed_ports)
        # draw table
        tables.draw_table(connectivity.connections)


def run(name: str, version: str):
    """
    This is our main function, it handles the entire program.
    If an error occurs within here, it returns with a fatal error
    to the program invocation.
    """
    # get the tomlfile path
    args = arguments.parse(name)
    servers_tomlfile = args.toml_file

    # get the time and initiate the log.
    date = time.asctime()
    log.write(f"[ START ]: {date}")
    if args.version:
        print(f"{name} ver. {version}")

    # get the servers information from the toml file and parse it
    servers = toml_parser.parse_toml(servers_tomlfile)
    log.write(f"TOML {servers_tomlfile} loaded!")

    # create threads and draw our initial table after threads.
    threads: list = __create_threads(servers, args.timeout)
    tables.draw_table(connectivity.connections, True)

    # start the threads
    for thread in threads:
        log.notify(f"[ Main Thread ]: {thread}")
        thread.start()

    # handle joining threads
    __join_threads(threads, timeout=args.timeout)

    # redraw the table one last time:
    tables.draw_table(connectivity.connections)

    if args.print_log:
        log.print_log()

    if args.output_log:
        log.write_log()
