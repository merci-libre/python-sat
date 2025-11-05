"""
Handles all port testing, and ICMP responses.

Generates a data structure for in/out connections, and for general port scans.
uses the following key/value formula:

    IP_address->
        [{ICMP_response}, {Ports_list}] <-Array values

For example, a list with connections will generate the following values:
    127.0.0.1->
        [True, [443,22]]
also creates and stores the hashmap dictionaries for the program:
```py
    # all tables stored within connectivity.py
    connectivity.connections={}
    connectivity.open_ports = {}
    connectivity.closed_ports = {}
```
"""
import socket
try:
    from . import log
    from .errors import eprint
except ImportError:
    import log
    from errors import eprint
# try importing our external dependencies
try:

    has_dep1 = False
    has_dep2 = False
    dep1 = "icmplib"
    dep2 = "requests"

    import icmplib
    has_dep1 = True
    import requests
    has_dep2 = True
except ModuleNotFoundError:
    eprint("\033[0;31m[ERROR]\033[0m: You are missing essential external"
           "libraries required to run this project.")
    if not has_dep1:
        eprint(f"Missing-> {dep1}")
    if not has_dep2:
        eprint(f"Missing-> {dep2}")

    exit(1)
except ImportError:
    eprint("\033[0;31m[ERROR]\033[0m: You are missing essential external"
           "libraries required to run this project.")
    if not has_dep1:
        eprint(f"Missing-> {dep1}")
    if not has_dep2:
        eprint(f"Missing-> {dep2}")
    exit(1)

# these are globally accessible throughout the entire program
connections = {}
open_ports = {}
closed_ports = {}


def test_http(ip_address: str, port: int, main_timeout: int) -> bool:
    log.write("attempting to connect via http...")
    try:
        response = requests.get(
            f"http://{ip_address}:{port}", timeout=main_timeout)
        log.write(f"ABLE TO CONNECT VIA HTTP to {ip_address}:{port}!")
        log.write(f"Connected to {port} via HTTP on {
                  ip_address}, response={response}")

        return True
    except requests.exceptions.Timeout:
        log.error(
            f"HTTP connection timed out for {ip_address} on port {port}")
        return False
    except requests.exceptions.ConnectionError:
        log.error(
            f"HTTP reached max retries for {ip_address} on port {port}")
        return False
    except Exception as e:
        log.error(
            f"HTTP connection to {port} for {ip_address} failed with the",
            f"following error message: {type(e).__name__}: {e}")
        return False


def test_ports(ip_address: str, timeout: int) -> None:
    """
    Test port connectivity, and appends them to a dictionary
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_list = connections.get(ip_address)[1]
    list_open = []
    list_closed = []
    for port in port_list:
        result = sock.connect_ex((ip_address, port))
        if result == 0 or test_http(ip_address, port, timeout):
            list_open.append(port)
            log.write(f"FROM TEST_PORTS: connected to {
                port} on {ip_address}!")
            open_ports[ip_address] = list_open
        else:
            log.error(f"[Port Testing]: unable to connect to {
                port} on {ip_address}...")
            list_closed.append(port)
            closed_ports[ip_address] = list_closed
        sock.close()


def ping(ip_address: str, main_timeout: int) -> bool:
    """
    Ping the given address with ICMP requests.
    """
    # pings the server, on ICMP echo reply +=1
    packets_received = icmplib.ping(
        ip_address, 2, 1,
        timeout=main_timeout,
        privileged=False).packets_received

    if packets_received > 0:
        return True
    else:
        return False


def test(ip_address: str, ports: list, scan: bool, timeout=4) -> None:
    """
    This is our "main" testing function, we load this function
    with data from the parsed toml file. T
    """
    try:
        # ping the address:
        ping_ok = ping(ip_address, timeout)

        # update our map
        if ping_ok:
            log.write(f"[ICMP Ping]: {ip_address} connected!")
            connections[ip_address] = [True, ports]
        else:
            log.error(f"[ICMP Ping]: {ip_address} did not connect...")
            connections[ip_address] = [False, None]
    except Exception as e:

        # any errors in ping will just update the values
        # as if it never connected.
        log.error(f"[ICMP Ping]: \n\tip_address= {
                  ip_address}\n\tports= {ports} \n{e}")
        connections[ip_address] = [False, None]
        return False
    if ports is not None and scan:
        test_ports(ip_address, timeout)
