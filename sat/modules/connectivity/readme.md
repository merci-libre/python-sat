# Connectivity Library
This folder contains all the code for making and receiving connections over
TCP, HTTP, and ICMP. ALl threads use this library when making connections to
servers through the `test()` function-- which makes calls to other functions
defined such as `ping()`, and `test_ports()`.

This module depends on `icmplib` and `requests`, and is the only library in the
entire project that requires external dependencies.

## Ping over ICMP
Before scanning the ports on a server, python-SAT first attempts to ping the server
over ICMP. If the server is not reachable, the thread will pre-emptively rejoin to main,
and forward a dictionary/hashmap containing information on the status of the connections.

The primary function that handles this functionality is the `ping()` function, which requires
the [icmplib](<https://github.com/ValentinBELYN/icmplib?tab=readme-ov-file#documentation>) library to make either privileged or unprivileged ICMP connections to servers.

That function gets handled in `main.py` through the `__join_threads()` function, of which
all global variables gets forwarded to the class `UpdateTables` in `tables.py`. 

## Socket connections
As of version 1.0, the only protocols that python-SAT supports is TCP and HTTP.
In future additions, python-SAT will be able to scan for UDP connectivity, and thus
this section of the readme will be updated. 

All socket connections get handled inside of the `test_ports()` function. This function
is responsible for updating the global variables `open_ports` and `closed_ports` dictionaries,
as well as updating the `connections` dictionary.

### TCP connectivity
Python-SAT checks if a server has a port open by the completion of the 4-way TCP handshake.
Of which, we iterate over a list defined by the user defined in a .toml file in the 
defined `ports` key. If no valid ports are detected, or if the value for `scan` is false, we skip
over testing the ports.

### HTTP connectivity
In addition to standard TCP connections, python-SAT is able to detect services 
using the HTTP protocol. We use the [requests](<https://requests.readthedocs.io/en/latest/>) library as a dependency to
complete this specific function.

This occurs inside of the `test_http()` function, and corrects the values that
`test_ports()` appends to the global `open_ports` dictionary.
