from . import ansi
from . import log
import sys
from .errors import eprint


class UpdateMaps():
    """
    This updates the port maps for the table.
    """
    open_ports = {}
    closed_ports = {}

    def __init__(self, open_ports: {}, closed_ports: {}):
        log.notify(f"[From UpdateMaps]: Open Port Tables: {
                   UpdateMaps.open_ports}")
        log.notify(f"[From UpdateMaps]: Closed Port Tables: {
                   UpdateMaps.closed_ports}")
        UpdateMaps.open_ports = open_ports
        UpdateMaps.closed_ports = closed_ports


class __globals:
    """
    Creates a global variable class for this module.
    Used to print the table, format it correctly, and
    does some 'funky' string wizardry.
    """
    # text
    lines_written = 0
    ip_address = "IP ADDRESS"
    icmp_message = "ICMP PING?"
    open_ports = "open ports"
    closed_ports = "closed ports"
    table_header = f" {ip_address}      {
        icmp_message}        {ansi.GREEN}[{open_ports}] ::  {ansi.RED}[{closed_ports}]{ansi.END}"

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


def __draw_ip_table_format(connections: dict,
                           ip_address: str,
                           count: int,
                           table_start: bool):
    """
    Draws out the table. Only available within this specific module.
    """
    responsive = connections.get(ip_address)[0]
    ports = UpdateMaps.open_ports.get(ip_address)
    closed_ports = UpdateMaps.closed_ports.get(ip_address)

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
    ip_bar = __globals.ip_bar
    connected_bar = __globals.connected_bar

    # ip address spacing
    ip_spacing = " "*(__globals.max_ip_length-ip_address.__len__())
    ip_address = f"{ansi.END}{ip_address}{ip_spacing}{__globals.table_color}"

    # get ports:

    # calculate ICMP response:
    if responsive is True:
        status = "OK"
        connected = f"{ansi.GREEN}{status}{__globals.table_color}"
    elif responsive == "awaiting":
        status = "awaiting..."
        connected = f"{ansi.LIGHT_BLUE}{status}{__globals.table_color}"
    else:
        status = "TIMED OUT"
        connected = f"{ansi.RED}{status}{__globals.table_color}"

    # ICMP response spacing
    con_spacing = " "*(__globals.max_con_length-status.__len__()+1)
    connected = f"{connected}{con_spacing}"

    # Table Divider:
    eprint(f"{__globals.table_color}{left_corner}{ip_bar}{
        divider}{connected_bar}{closer}{ansi.END}")
    # Table Entry:
    eprint(f"{__globals.table_color}┃{ip_address}┃{
        connected} ┃ ==> {ansi.GREEN}{ports} :: {ansi.RED}{closed_ports}{ansi.END}")
    __globals.lines_written += 2


def clear_table():
    log.notify("CLEARING TABLES")
    for i in range(__globals.lines_written):
        sys.stderr.write('\x1b[1A')
        sys.stderr.write('\x1b[2K')
    __globals.lines_written = 0


def draw_table(ip_list: dict, initial=False):
    """
    Updates the table with values, and draws the table
    this value is callable from main
    """
    count = 0
    if not initial:
        clear_table()
    eprint(__globals.table_header)
    for ip_address in ip_list.keys():
        __draw_ip_table_format(ip_list, ip_address, count, initial)
        count += 1
    eprint(__globals.bottom)
    __globals.lines_written += 2
