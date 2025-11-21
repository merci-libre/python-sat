# Westwardfishdme's Server Administration Tool (sat)
A CLI server administration tool designed to check server uptimes,
open ports, and available system services. Allows a user to
maintain a list of connected servers.

Check the supported Operating Systems here: 

| OS              | Install script | PIP support | Tested?   | Supported | 
| --------------- | -------------- | ----------- | --------- | --------- |
| Debian Linux    | (✅)           | VENV only   | (✅)      | (✅)      |
| Ubuntu          | (✅)           | VENV only   | (✅)      | (✅)      |
| Arch Linux      | (✅)           | VENV only   | (✅)      | (✅)      |
| Gentoo          | (❌)           | VENV only   | (❌)      | (❌)      |
| OpenSUSE        | (❌)           | VENV only   | (❌)      | (❌)      |
| RHEL-based      | (❌)           | VENV only   | (❌)      | (❌)      |
| MacOS           | (✅)           | (✅)        | (✅)      | (✅)      |
| Windows (❌)    | (❌)           | None        | (❌)      | (❌)      |


# Table of Contents
**About**
- [Description](<#Description>)
- [Requirements](<#Requirements>)
- [Installation](<#Installation>)
  - [Install Script](<#Using-the-provided-installation-script-RECOMMENDED>)
  - [Building from source](<#Building-from-source>)
  - [Uninstalling](<#Uninstalling>)

**Commands**
- [Command list](<#list-of-commands>)
  - [Configuration Options](<#configuration-options>)
  - [Informational Options](<#informational-options>)

**Configuration**
- [toml file configuration](<#server-list>)
- [Server List Formatting](<#Server-List-Formatting>)
- [Valid Key/Value Pairs](<#Valid-KeyValue-pairs>)

**Contributing**
- [Contributing](<#Contributing>)
- [Licensing](<#Licensing>)
- [Reporting Issues](<#Reporting-Issues>)


# Requirements
`python-sat` was developed and tested on Arch and Debian Linux on python **version 3.13.7** 
however, versions >3.11 should be sufficient enough.

**__Windows installations do not work natively__** (as of sat v1.2)

[Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/)
is highly recommended to use this tool, mostly to
avoid any unforseen issues.

## Dependencies
`python-sat` requires 2 external libraries:
1. icmplib
2. requests

Installation with pip requires `setuptools`, `build`, and the installation
of the above dependencies.

These can be downloaded through the system package manager or through the install script.

```sh
pip install -r requirements.txt
```
## Windows

Due to how the tables are printed with specific UNICODE characters, 
Windows will not receive direct support for `python-sat` until a later
version either fixes this, or you fork the repository and fix the tables
yourself. It is not a priority for me to add functionality for windows, so
please do not spam this as an issue. 

If you wish to still install `python-sat`,
please use the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install)
before proceeding to install `python-sat`

# Installation
First, clone the repository:
```sh
git clone https://github.com/merci-libre/python-sat
```
Go to the directory.

```sh
cd python-sat
```

Then choose one of the following options below.

- [Install Script](<#Using-the-provided-installation-script-RECOMMENDED>)
- [Building from source](<#Building-from-source>)

If you wish to uninstall python-sat, read the [uninstall section](<#uninstalling>).

## Using the provided installation script (RECOMMENDED)
First, see if your Operating system is compatible for the install script:

| OS              | Install script | PIP support | Tested?   | Supported |
| --------------- | -------------- | ----------- | --------- | --------- |
| Debian          | (✅)           | VENV only   | (✅)      | (✅)      |
| Ubuntu          | (✅)           | VENV only   | (✅)      | (✅)      |
| Arch            | (✅)           | VENV only   | (✅)      | (✅)      |
| Gentoo          | (❌)           | VENV only   | (❌)      | (❌)      |
| OpenSUSE        | (❌)           | VENV only   | (❌)      | (❌)      |
| RHEL-based      | (❌)           | VENV only   | (❌)      | (❌)      |
| MacOS           | (✅)           | Unknown     | (✅)      | (✅)      |

To install `sat`, use the provided `install.py` with:

This should create both the configuration files, and attempt
to install the dependencies for the project. If installing the
dependencies fails, it will create the directories regardless;

```
python install.py
```

## Building from source 

You can also use the provided `pyproject.toml` build file to build the project with pip:
This guide requires that you install the following dependencies:

- pip `version >= 24.0.0`
- build `version >= 1.3.0`
- setuptools `version >= 1.3.0`

install the requirements:
```sh
pip install -r requirements.txt
```

Build the wheel file:
```sh
# Make sure you have build and setuptools installed!
# build the wheel file
python -m build
```

install the package with pip

```sh
# install with pip
pip install .
```

# Dependencies using system packages.

It is highly recommended that you run the install script or get the packages
through your system's package manager. To see more information, read the section
below titled.


In addition, `requests` does require some external packages.

## System Packages
If you are on Arch Linux, or another distribution which
requires external python libraries to be installed with
the system Package Manager, please install the following 
python libraries:

```
icmplib 
requests
setuptools
build
```

On Debian/Ubuntu:
```
# apt-get install python3-icmplib python3-requests python3-build python3-setuptools
```
On Arch Linux:
```
# pacman -S python-icmplib python-requests python-build python-setuptools
```

# Uninstalling
To uninstall python sat, simply run the following command:

```sh
./install.sh --uninstall
```
# Usage

After installing `sat` you can just invoke the command with
`python sat` within the project/repositories root directory.

example:
```sh
# in the root repo directory...
python sat
```
or if you installed via the install script:
```sh
sat.py -h # show help command.
```

# List of Commands

Here is a list of arguments you can use to run `sat`:

```
usage: sat [options] [-t [TOML_FILE]]

options:
  -h, --help            show this help message and exit
  --stderr, -s          Output the final table connection to stderr.
  --verbose, -v         prints a log at runtime
  --output-log, -o OUTPUT_LOG
                        outputs a log to the current directory, as a filename
  --new, -n NEW         creates a new toml file in the current working
                        directory.
  --toml-file, -t [TOML_FILE]
                        Toml file to get parsed. If none specified, use
                        default
  --timeout, -T [TIMEOUT]
                        Set the timeout (in seconds)
  --version, -V         print the version

```

If no arguments are passed, `sat` will print out a table containing diagnostic information for each server found
inside of the default `servers.toml` directory.

# Configuration

## Server List

Server lists are a configuration file written in `.toml` that are located
within a default directory depending on the Operating System that you install
this tool on.


### On OSX/Linux/WSL:
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

# Contributing
To contribute to this project please fork the repository or add any suggestions through the
[issues](https://github.com/merci-libre/python-sat/issues) tab and list the idea as an enhancement.
otherwise please read the [licensing](<#Licensing>) section down below.

## Licensing
As per the license agreement with the GPL-version 2.0, you as the user are not only allowed
to view and audit the source code of this project, but any contributions made in forks of the
code must be publically accessible and disclosed as per described in section 3 of the 
GPL-v.2 license. Any source code published must maintain in accordance with the GPL-v2.

If you do fork this repository, please credit this original repository in the readme.
Thanks!

## Reporting Issues
If you encounter a bug while running this project, please submit a bug-report to
the [issues](https://github.com/merci-libre/python-sat/issues) tab.

I'll try to fix as much as I can, however if you have code available that fixes an issue--
fork the repository, make the additions, and submit a pull-request. (not yet implemented)

