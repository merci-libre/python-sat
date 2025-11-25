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
import threading
try:
    import log
    from errors import eprint
    import errors
except ModuleNotFoundError:
    import sat.modules.log as log
    from sat.modules.errors import eprint
    import sat.modules.errors as errors
# try importing our external dependencies
try:
    has_dep1 = False
    has_dep2 = False

    import icmplib
    has_dep1 = True
    import requests
    has_dep2 = True

except ImportError:
    """
    Use the built-in dependencies
    NOTICE: these packages were installed
    through the venv, and are not updated.
    Notify the user to try and install them
    directly.
    """
    from . import ansi
    eprint(f"{ansi.YELLOW}[NOTICE]{
           ansi.END} install the dependencies please!:")
    if not has_dep1:
        print("icmplib")
    if not has_dep2:
        print("requests")
    exit(1)


# these are globally accessible throughout the entire program
connections = {}
open_ports = {}
closed_ports = {}


def test_http(ip_address: str, port: int, main_timeout: int) -> bool:
    """
    Tests to see if an HTTP server is responsive on the server.
    Even if it 404's python-SAT will still consider it to be 'up'
    may at a later date add a feature to catch this response, and
    return a message to the user with more details on the response.
    """
    log.notify(f"attempting to connect via http to {
               ip_address} on port {port}...")
    # stores the value for the true response.
    http_response = False

    try:
        status = requests.get(
            f"http://{ip_address}:{port}", timeout=main_timeout)

        # previous function can fail.
        log.write(f"[http]: ABLE TO CONNECT VIA HTTP to {ip_address}:{port}!")
        log.info(f"Connected to {port} via HTTP on {
                 ip_address}, status={status}")
        http_response = True

    except requests.exceptions.Timeout:
        log.error(
            f"[http]: HTTP connection timed out for {
                ip_address} on port {port}")
        http_response = False

    except requests.exceptions.ConnectionError:
        log.error(
            f"[http]: HTTP reached max retries for {
                ip_address} on port {port}")
        http_response = False

    except Exception as e:
        log.error(
            f"HTTP connection to {port} for {ip_address} failed with the",
            f"following error message: {type(e).__name__}")

    # free the memory, return the response
    del ip_address, port, main_timeout
    return http_response


def test_ports(ip_address: str, port: int, timeout: int) -> None:
    """
    Test port connectivity, and appends them to a dictionary
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    list_open = open_ports.get(ip_address)
    list_closed = closed_ports.get(ip_address)
    result = sock.connect_ex((ip_address, port))

    if result == 0 or test_http(ip_address, port, timeout):
        log.write(f"[ports]: connected to {port} on {ip_address}!")
        list_open.append(port)

    else:
        log.error(f"[ports]: unable to connect to {port} on {ip_address}...")
        list_closed.append(port)
    sock.close()

    open_ports[ip_address] = list_open
    closed_ports[ip_address] = list_closed


def ping(ip_address: str, main_timeout: int, max_packets_sent=5) -> bool:
    """
    Ping the given address with ICMP requests.
    """
    response = False

    # pings the server, on ICMP echo reply +=1
    packets_received = 0

    for packets_sent in range(1, max_packets_sent):

        # here we check if we need to make a privilege socket
        try:
            packets_received += icmplib.ping(
                ip_address, count=1, interval=0.8,
                timeout=main_timeout,
                privileged=True).packets_received

        except icmplib.exceptions.SocketPermissionError:
            packets_received += icmplib.ping(
                ip_address, count=1, interval=0.8,
                timeout=main_timeout,
                privileged=False).packets_received

        else:
            raise errors.Connection.Privileges

        # if by the second iteration, we have 0 packets_received just break.
        if packets_received == 0 and packets_sent == 2:
            break

    # we subtact 1 from max_packets_sent to account for the 0 offset for
    # iterables.
    dropped = f"{(1.0-(packets_received/(max_packets_sent-1)))*100:.2f}%"

    log.notify(f"Pinged {ip_address} with {packets_sent}...")

    if packets_received > 0:
        log.write(f"[ping]: {ip_address} is up!")
        response = True

    else:
        log.error(f"{ip_address} responded with {packets_received} packets")
    log.info(f"ip: {ip_address}, packet_loss:{
        dropped}, timeout:{main_timeout}, packets_sent:{
        packets_sent}")

    # free the memory, return the response
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
        # we don't need to scan the ports if neither value.
        if ports is not None and scan:
            port_list = connections.get(ip_address)[1]
            list_open = []
            list_closed = []

            open_ports[ip_address] = list_open
            closed_ports[ip_address] = list_closed
            log.notify(f"checking port status on {
                       ip_address} on ports: {ports}")
            # create subthreads for port scanning
            threads = []
            for port in port_list:
                t = threading.Thread(
                    target=test_ports(
                        ip_address, port, timeout),
                )
                t.daemon = True
                threads.append(t)

            # start the subthreads
            for thread in threads:
                thread.start()
                thread.join(timeout)
            log.notify(f"open_ports: {open_ports}")
            log.notify(f"closed_ports: {closed_ports}")

        return  # stop and rejoin the main thread.

    except Exception as e:
        log.error(e)

    # kill the thread
    return
