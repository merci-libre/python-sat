"""
This module is responsible for handling the printing of the table
to STDOUT/STDERR.
"""
try:
    import sat.modules.ansi as ansi
    import sat.modules.log as log
except ModuleNotFoundError:
    import modules.ansi as ansi
    import modules.log as log

import sys


class UpdateTables():
    """
    This updates the port maps for the table.
    """
    open_ports = {}
    closed_ports = {}
    connections = {}

    def __init__(self, open_ports: {},
                 closed_ports: {},
                 connections: {}):
        UpdateTables.open_ports = open_ports
        UpdateTables.closed_ports = closed_ports
        UpdateTables.connections = connections


class __globals:
    """
    Creates a global variable class for this module.
    Used to print the table, format it correctly, and
    does some string wizardry.
    """
    # text
    class Text:
        lines_written = 0
        ip_address = "IP ADDRESS"
        icmp_message = "ICMP PING?"
        open_ports = "open ports"
        closed_ports = "closed ports"
        table_header = f" {ip_address}      {icmp_message}        {
            ansi.GREEN}[{open_ports}] :: {ansi.RED}[{closed_ports}]{ansi.END}"
        # for calculations
        max_ip_length = "000.000.000.000".__len__()
        max_con_length = "awaiting...".__len__()-1
        # bar strings
        ip_bar = '━' * max_ip_length
        connected_bar = '━'*(max_con_length+2)
        pure_ip_space = " " * max_ip_length
        pure_connect_sp = ' ' * max_con_length
        # TABLE COLORING
        table_color = ansi.BLUE
        # this is the bottom bar.
        bottom = f"{table_color}┗{ip_bar}┻{connected_bar}┛{ansi.END}"


def __draw_ip_table_format(ip_address: str,
                           count: int, sysfile):
    """
    Draws out the table. Only available within this specific module.
    sysfile=sys.stdout || sys.stderr
    """
    ports = UpdateTables.open_ports.get(ip_address)
    closed_ports = UpdateTables.closed_ports.get(ip_address)
    responsive = UpdateTables.connections.get(ip_address)[0]
    # if the closed ports or open ports
    # are an empty list, format the list
    # to look pretty.
    if closed_ports == []:
        closed_ports = None
    if ports == []:
        ports = None

    # fix ip address length
    if ip_address.__len__() > __globals.Text.max_ip_length:
        ip_address = f"{ip_address[:(__globals.Text.max_ip_length-3)]}..."

    match count:
        # top
        case 0:
            left_corner = "┏"
            divider = "┳"
            closer = "┓"
        # elsewhere
        case _:
            left_corner = "┣"
            divider = "╋"
            closer = "┫"

    """
    Variables get renamed so that the formatting list is slightly more readable
    """

    # bars
    ip_bar = __globals.Text.ip_bar
    connected_bar = __globals.Text.connected_bar

    # ip address spacing
    ip_spacing = " "*(__globals.Text.max_ip_length-ip_address.__len__())
    ip_address = f"{ansi.END}{ip_address}{
        ip_spacing}{__globals.Text.table_color}"

    # get ports:

    # calculate ICMP response:
    match responsive:
        case "awaiting":
            status = "awaiting..."
            connected = f"{ansi.LIGHT_BLUE}{
                status}{__globals.Text.table_color}"

        case True:
            status = "OK"
            connected = f"{ansi.GREEN}{status}{__globals.Text.table_color}"

        case _:
            status = "TIMED OUT"
            connected = f"{ansi.RED}{status}{__globals.Text.table_color}"

    # free some heap memory.
    del responsive

    # ICMP response spacing
    con_spacing = " "*(__globals.Text.max_con_length-status.__len__()+1)
    connected = f"{connected}{con_spacing}"

    # Table Divider:
    print(f"{__globals.Text.table_color}{left_corner}{ip_bar}{
        divider}{connected_bar}{closer}{ansi.END}", file=sysfile)
    # Table Entry:
    print(f"{__globals.Text.table_color}┃{ip_address}┃{
        connected} ┃ ==> {ansi.GREEN}{ports} :: {ansi.RED}{closed_ports}{ansi.END}",
        file=sysfile)
    __globals.Text.lines_written += 2


def clear_table(stderr: bool):
    """
    Clears the table
    the parameter 'output'
    maps to stdout or stdin.
    """
    if stderr:
        log.notify("CLEARING TABLES")
        for i in range(__globals.Text.lines_written):
            sys.stderr.write('\x1b[1A')
            sys.stderr.write('\x1b[2K')
        __globals.Text.lines_written = 0
    else:
        log.notify("CLEARING TABLES")
        for i in range(__globals.Text.lines_written):
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')
        __globals.Text.lines_written = 0


def get_lines():
    return __globals.Text.lines_written


def draw_table(initial=False, stderr=False):
    """
    This function updates the table with values, and draws the table
    this value is called in main.py returns the count of the lines written.
    """

    count = 0
    if not initial:
        clear_table(stderr)

    # we have to print the top and
    # bottom headers outside of the table.
    sysfile = sys.stdout
    if stderr:
        sysfile = sys.stderr

    print(__globals.Text.table_header, file=sysfile)
    for ip_address in UpdateTables.connections.keys():
        __draw_ip_table_format(ip_address, count, sysfile)
        count += 1
    print(__globals.Text.bottom, file=sysfile)
    __globals.Text.lines_written += 2
