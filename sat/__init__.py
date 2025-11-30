# for setuptools to install the package.
from .modules import (
    main,
    connectivity,
    log,
    errors,
    toml,
    tables,
    ansi,
    arguments,
)
from .sat import start


import os
import pathlib


def make_config():
    """
    although it says linux/windows, it is system agnostic
    """
    POSIX = (os.name == "posix")
    MACOS = (os.name == "darwin")
    WINDOWS = (os.name == "nt")
    homedir = f"{pathlib.Path.home()}"
    configuration = ""

    if POSIX or MACOS:
        configuration = "/.config/server_admin_tool/"

    if WINDOWS:
        # Windows must use WSL for the time being.
        """
        if INSTALLFLAGS.config_dir == "default":
            configuration = f"\\Documents\\server_admin_tool\\"
        else:
            configuration = INSTALLFLAGS.config_dir
        """
        print("It looks like you did not read the readme.")
        raise Exception("On Windows, please read the readme.")

    if homedir == "" or configuration == "":
        raise Exception
    path_to_config = f"{homedir}{configuration}"

    return path_to_config


def create_servers_toml(config_dir: str):
    with open(f"{config_dir}servers.toml", 'w') as toml:
        toml.write("[servers]\n")
        toml.write("\n[servers.localhost]")
        toml.write('\n\tip = "127.0.0.1"')
        toml.write('\n\tports=[22,443,8080]')
        toml.write('\n\tscan=true')
        toml.write("\n[servers.localhost2]")
        toml.write('\n\tip="localhost"')
        toml.write('\n\tports=22')
        toml.write('\n\tscan=false')
        toml.write("\n[servers.google_dns]")
        toml.write('\n\tip="8.8.8.8"')
        toml.write('\n\tscan=false')

    print(f"default: {config_dir}servers.toml was created.")


config_dir = make_config()

if not os.path.exists(config_dir):
    os.makedirs(config_dir)
    print(f"created configuration directory @ {config_dir}")

dirvider = "/"

if os.path.exists(f"{config_dir}{dirvider}servers.toml"):
    pass
else:
    print(f"creating servers.toml in {config_dir}")
    create_servers_toml(config_dir)
    print("Please re-run python-sat!")
