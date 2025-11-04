# Westwardfishdme's Server Administration Tool (sat)
**About**
- [Description](readme#Description)
- [Installation](readme#Installation-Dependencies)
**Commands**
- [Command list](<readme#List of Commands>)
  - [Interactive Options](<readme#interactive options>)
  - [Testing Options](<readme#testing options>)
  - [Configuration Options](<readme#configuration options>)
  - [Informational Options](<readme#informational options>)

**Configuration**
- [Client Configuration (Servers)](<readme#server list>)
  - [Server List Formatting](<readme#Server List Formatting>)
  - [Valid Key Value Pairs](<readme#Valid Key/Value pairs>)
## Description
A CLI server administration tool designed to check server uptimes,
open ports, and available system services. Allows a user to
maintain a list of connected servers (up to a max of 10 per page).


# Installation/Dependencies

To install `sat`, use the provided `install.py` with:

This should create both the configuration files, and attempt
to install the dependencies for the project. If installing the
dependencies fails, it will create the directories regardless;

```
python install.py
```

## External Python VENV or using system packages.
If you are on Arch Linux, or another distribution which
requires external python libraries to be installed with
the system Package Manager, please install the following 
python libraries:

```
icmplib
requests
```

On Arch Linux:
```
# pacman -S python-icmplib python-requests
```

The program requires an SUID bit signature for the `connectivity` module, which
uses raw sockets to 

# List of Commands

`sat` allows you to do numerous amounts of tests, benchmarking (not yet implemented), 
and 

Here is a list of arguments you can use to run `sat`:

### Interactive options
- `--interactive-mode (-I)`: Launches an interactive mode shell-like environment.
- `--sort (-S)` : Sort tables by CIDR block format /24 (e.g. any ip address with 127.0.0.* will list out a specific table for the ip range 127.0.0.0/24)

### Testing options
- `--connect (-c) <SERVICE_PORT>`: Attempt to connect to a specific port on the machine
- `--test-mode (-T)`: Automatically test services on ALL listed ports in `check_ports` 
value inside of the `server_list.toml` file (currently only tests HTTP(S), SSH, and ICMP protocol)

### Configuration options

- `--new (-n)`: start an interactive prompt to create a new server to append to the `server_list.toml` file.
- `--delete (-X)`: remove 

### Informational options

- `--verbose (-v)`: be verbose.
- `--version (-V)`: Print Version information.

If no arguments are passed, `sat` will print out a table containing diagnostic information on each server found
inside of `{CONFIG_DIRECTORY}/`

# Configuration

## Server List

Server lists are a configuration file written in `.toml` that are located
within a default directory depending on the Operating System that you install
this tool on.

### On Windows:
For Windows users, it will create a file within the directory:

`C:\Documents\ServerAdminTool\serverlists\server_list.toml`

### On OSX/Linux:
For MacOS, and Linux users:

`$HOME/.config/ServerAdminTool/serverlists/server_list.toml`

On startup, `sat` will search for these files within those directories. 
If the process cannot find the file, the program will generate an error, 
and exit.


## Server List Formatting
By default, the first IP will always be set to the loopback
address. This is to test functionality within the program itself, but
also to describe how you should add servers in to this file.

```toml
[Server]
  [server.localhost]
  ip_address= "127.0.0.1" # server ip address
  check_ports=[443, 8080, 22] # checks if the TCP ports in this list are open

  [server.google_dns]
  ip_address= "8.8.8.8" # server ip address
  scan= False

```
You can either append to this list manually, or use the command line to create
a new entry.

### Valid Key/Value pairs
As of of this current release version, the table below lists
accepted keys and types for value pairs, and a description of
what `sat` interprets the information within `server_list.toml`.

| Key             | Value Types     | Description         | Example         |
| --------------- | --------------- | ------------------- | --------------- |
| `ip_address`    | String          | Server IP address   | "127.0.0.1"     |
| `ports`         | List[int]       | TCP ports to check  | `[443, 22]`     |
| `scan`          | Boolean         | Allow Port Scan?    | `True/False`    |

**EXAMPLES**
- `ip_address`: "192.168.0.1" or "https://google.com", or (hostname) in `/etc/hosts`.
- `hostname`  : "foobar"
- `check_ports`: `[443, 22, 21]` or `[None]` or `None`
