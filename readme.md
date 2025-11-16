# Westwardfishdme's Server Administration Tool (sat)
**About**
- [Description](<#Description>)
- [Requirements](<#Requirements>)
- [Installation](<#Installation>)

**Commands**
- [Command list](<#list-of-commands>)
  - [Configuration Options](<#configuration-options>)
  - [Informational Options](<#informational-options>)

**Configuration**
- [toml file configuration](<#server-list>)
- [Server List Formatting](<#Server-List-Formatting>)
- [Valid Key/Value Pairs](<#Valid-KeyValue-pairs>)

# Description
A CLI server administration tool designed to check server uptimes,
open ports, and available system services. Allows a user to
maintain a list of connected servers.

## Requirements
`python-sat` was developed and tested on python **version 3.13.7**
however, version >3.11  should be sufficient enough.

## Dependencies
`python-sat` requires 2 external libraries:
1. icmplib
2. requests

These can be downloaded through pip or installed via the `requirements.txt`

If your python version requires an external python-venv, see [this section](<#external-python-venv-or-using-system-packages>)

# Installation
First, clone the repository:
```sh
git clone https://github.com/merci-libre/python-sat
```
Go to the directory.

```sh
cd python-sat
```

To install `sat`, use the provided `install.py` with:

This should create both the configuration files, and attempt
to install the dependencies for the project. If installing the
dependencies fails, it will create the directories regardless;

```
python install.py
```

## External Python VENV or using system packages.

To install this package within the python VENV, you can use the VENV tools within
your specific python venv directory.

# System Packages
If you are on Arch Linux, or another distribution which
requires external python libraries to be installed with
the system Package Manager, please install the following 
python libraries:

```
python-icmplib 
python-requests
```

On Debian/Ubuntu:
```
# apt-get install python-icmplib python-requests
```
On Arch Linux:
```
# pacman -S python-icmplib python-requests
```
# Usage

After installing `sat` you can just invoke the command with
`python sat` within the project/repositories root directory.

A system wide implentation has not been added yet.

example:
```sh
# in the root repo directory...
python sat -v -t my_servers.toml
```

# List of Commands

Here is a list of arguments you can use to run `sat`:

### Testing options
- `--toml-file | -t {path/to/file.toml}`: use a non-default toml file (that is not servers.toml)
- `--timeout | -T {int} (DEFAULT: 4)`: Default timeout for connections, default value is 4

### Informational options

- `--print-table | -v`: prints a log to standard out
- `--output-log | -o {file}`: outputs a log to /tmp/ directory, (will change to current directory in v1.01)
- `--version | -V`: Print software and version information.
- `--help | -h`: print help

If no arguments are passed, `sat` will print out a table containing diagnostic information for each server found
inside of the default `servers.toml` directory.

# Configuration

## Server List

Server lists are a configuration file written in `.toml` that are located
within a default directory depending on the Operating System that you install
this tool on.

### On Windows:
For Windows users, it will create a file within the directory:

`C:\Documents\server_admin_tool\servers.toml`

### On OSX/Linux:
For MacOS, and Linux users:

`$HOME/.config/server_admin_tool/servers.toml`

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
  check_ports=[443, 8080, 22] # checks if the TCP ports in this list are open,

  [server.google_dns]
  ip_address= "8.8.8.8" # server ip address
  scan= false

```
You can either append to this list manually, or use the command line to create
a new entry.

### Valid Key/Value pairs
As of of this current release version, the table below lists
accepted keys and types for value pairs, and a description of
what `sat` interprets the information within `servers.toml`.

| Key             | Value Types     | Description         | Example         |
| --------------- | --------------- | ------------------- | --------------- |
| `ip_address`    | String          | Server IP address   | "127.0.0.1"     |
| `ports`         | List[int]       | TCP ports to check  | `[443, 22]`     |
| `scan`          | Boolean         | Allow Port Scan?    | `True/False`    |

**EXAMPLES**
- `ip_address`: "192.168.0.1" or "https://google.com", or (hostname) in `/etc/hosts`.
- `hostname`  : "foobar"
- `ports`: `[443, 22, 21]`
- `scan`: True

