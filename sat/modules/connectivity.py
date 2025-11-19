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
    # all hashmaps stored within connectivity.py
    connectivity.connections={}
    connectivity.open_ports ={}
    connectivity.closed_ports ={}
```
"""
import socket
import time
try:
    from . import log
    from .errors import eprint
    from . import errors
except ImportError:
    import log
    import errors
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
    """
    Use the built-in dependencies
    NOTICE: these packages were installed
    through the venv, and are not updated.
    Notify the user to try and install them
    directly.
    """
    from .external import requests
    from .external import icmplib

# these are globally accessible throughout the entire program
connections = {}
open_ports = {}
closed_ports = {}


def test_http(ip_address: str, port: int, main_timeout: int) -> bool:
    log.write("attempting to connect via http...")
    rs = False
    try:
        response = requests.get(
            f"http://{ip_address}:{port}", timeout=main_timeout)
        log.write(f"[http]: ABLE TO CONNECT VIA HTTP to {ip_address}:{port}!")
        log.info(f"Connected to {port} via HTTP on {
                 ip_address}, response={response}")
        rs = True
    except requests.exceptions.Timeout:
        log.error(
            f"[http]: HTTP connection timed out for {ip_address} on port {port}")
        rs = False
    except requests.exceptions.ConnectionError:
        log.error(
            f"[http]: HTTP reached max retries for {ip_address} on port {port}")
        rs = False
    except Exception as e:
        log.error(
            f"HTTP connection to {port} for {ip_address} failed with the",
            f"following error message: {type(e).__name__}")
    del ip_address, port, main_timeout
    return rs


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
            log.notify(f"[ports]: connected to {port} on {ip_address}!")
            open_ports[ip_address] = list_open
        else:
            log.error(f"[ports]: unable to connect to {
                port} on {ip_address}...")
            list_closed.append(port)
            closed_ports[ip_address] = list_closed
        sock.close()


def ping(ip_address: str, main_timeout: int, count=4) -> bool:
    """
    Ping the given address with ICMP requests.
    """
    response = False
    # pings the server, on ICMP echo reply +=1
    try:
        packets_received = icmplib.ping(
            ip_address, count, 0.8,
            timeout=main_timeout,
            privileged=True).packets_received
    except icmplib.exceptions.SocketPermissionError:
        packets_received = icmplib.ping(
            ip_address, count, 0.8,
            timeout=main_timeout,
            privileged=False).packets_received
    else:
        raise errors.Connection.Privileges

    dropped = f"{(1.0-packets_received/count)*100:.2f}%"
    log.notify(f"Pinged {ip_address} with {count}...")

    if packets_received > 0:
        log.write(f"[ping]: {ip_address} is up!")
        log.info(f"ip: {ip_address}, packet_loss:{
                 dropped}, timeout:{main_timeout}")
        response = True
    else:
        log.error(f"{ip_address} responded with {packets_received} packets")
        log.info(f"ip: {ip_address}, packet_loss:{
                 dropped}, timeout:{main_timeout}")
    del dropped, main_timeout, ip_address, packets_received
    return response


def test(ip_address: str, ports, scan: bool, timeout=4) -> None:
    """
    This is our "main" testing function, we load this function
    with data from the parsed toml file. T
    """
    try:
        # ping the address:
        ping_ok = ping(ip_address, timeout)

        if ping_ok:
            connections[ip_address] = [True, ports]
        else:
            connections[ip_address] = [False, None]
            return  # stop the thread
        del ping_ok
    except Exception as e:
        # any errors in ping will just update the values
        # as if it never connected.
        log.error(f"[Test][Ping]: {e}")
        connections[ip_address] = [False, None]
        return False

    try:
        if ports is not None and scan:
            log.notify(f"checking port status on {
                       ip_address} on ports: {ports}")
            test_ports(ip_address, timeout)
        else:
            return  # stop the thread
    except Exception as e:
        log.error(e)
        return
