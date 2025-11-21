#!/usr/bin/env python3
import time
import os
import sys
import pathlib

# XDG COMPLIANT


# installation flags.
class INSTALLFLAGS:
    """
    Change these if you would like to change
    any of the installation settings.
    """

    # XDG compliant directory
    config_dir = 'default'
    # install to system. (LINUX ONLY)
    system_install = True


def create_servers_toml(config_dir: str):
    with open(f"{config_dir}servers.toml", 'w') as toml:
        toml.write("[servers]\n")
        toml.write("\n[servers.localhost]")
        toml.write('\n\tip = "127.0.0.1"')
        toml.write('\n\tports=[22,443,8080]')
        toml.write('\n\tscan=true')
        toml.write("\n[servers.localhost2]")
        toml.write('\n\tip="localhost"')
        toml.write('\n\tport=22')
        toml.write('\n\tscan=false')
        toml.write("\n[servers.google_dns]")
        toml.write('\n\tip="8.8.8.8"')
        toml.write('\n\tscan=false')

    print(f"{config_dir}servers.toml was created.")


def make_config():
    """
    although it says linux/windows, it is system agnostic
    """
    LINUX = (os.name == "posix")
    WINDOWS = (os.name == "nt")
    homedir = f"{pathlib.Path.home()}"
    configuration = ""

    if LINUX:
        if INSTALLFLAGS.config_dir == "default":
            configuration = "/.config/server_admin_tool/"
        else:
            configuration = INSTALLFLAGS.config_dir

    if WINDOWS:
        # Windows must use WSL for the time being.
        """
        if INSTALLFLAGS.config_dir == "default":
            configuration = f"\\Documents\\server_admin_tool\\"
        else:
            configuration = INSTALLFLAGS.config_dir
        """
        print("It looks like you did not read the readme.")
        print("Please use the .")

    if homedir == "" or configuration == "":
        raise Exception
    path_to_config = f"{homedir}{configuration}"

    return path_to_config


class ReadOneChar:

    def __init__(self):
        import tty
        import sys
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            choice = sys.stdin.read(1)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        match choice:
            case '1':
                self.choice = "sudo"
            case '2':
                self.choice = "doas"
            case 'q' | 'Q':
                exit(0)
            case _:
                print(f"{choice} unknown input, please try again",
                      file=sys.stderr)
                raise ValueError


def system_install_unix(major: int, minor: int):
    """
    Installs the system packages via the install.sh
    script provided in the directory.

    Only allowed for POSIX based machines at the moment.
    """
    lib_path = f"/usr/lib/python{major}.{
        minor}/site-packages/serveradmintool"
    bin_path = "/usr/local/bin"
    # do a system install for linux machines.
    if os.name == "posix" and INSTALLFLAGS.system_install:
        sudo = False
        doas = False
        command = "sudo"
        if os.path.exists("/sbin/sudo"):
            print("sudo detected...")
            command = "sudo"
            sudo = True
        if os.path.exists("/sbin/doas"):
            print("doas detected...")
            doas = True
            command = "doas"

        if sudo and doas:
            while True:
                print("\nyou have both `sudo` and `doas` on your machine!")
                print("please select one option to continue:\n")
                print("[1] sudo")
                print("[2] doas")
                print("[q]uit\n")
                try:
                    sys.stderr.write("choice: \n")
                    choice = ReadOneChar().choice
                except ValueError:
                    continue
                command = choice
                break

            print(f"Running ./install.sh with {command}")

        print(f"installing libraries to {lib_path}")
        print(f"installing sat to {bin_path}")
        os.system(f"{command} ./install.sh {bin_path} {lib_path}")
    if os.name == "nt":
        print("[ERROR] system installs are only allowed for macos/linux",
              "at the moment, sorry...")
        print("however you can use WSL if you'd like :) ")


def install():
    dependencies = ["icmplib", "requests"]
    """
    installs the program.
    """
    # get dependencies
    print(f"installing sat for {sys.platform} machines")

    try:
        import icmplib
        import requests
    except ImportError:
        print("As of python-sat version 1.2,",
              "you don't need the dependencies,", file=sys.stderr)
        print("however-- it is highly recommended that you use,"
              "the your system package manager to install", file=sys.stderr)
        print("the packages as system packages, or through the venv--",
              "as the external libraries inside of this repository", file=sys.stderr)
        print("will not be updated in future versions.", file=sys.stderr)

        print("\n{package_manager_install} python-icmplib python-requests")
        print("(on debian systems): apt-get install",
              "python-icmplib python-requests")
        print("\nIf you are on windows, please follow the build instructions",
              "in the readme.md installation section titled ## Windows")
        time.sleep(4)

        if os.name == "nt":
            print("someone did not read the readme...")
            print("install WSL for windows, and use linux for python-sat!")
            print("https://learn.microsoft.com/en-us/windows/wsl/install")
            print("\nFor the easiest to use, get Ubuntu Linux for WSL.")
            exit(1)
    config_dir = make_config()

    try:
        os.makedirs(config_dir)
        print(f"created configuration directory @ {config_dir}")
    except FileExistsError:
        pass

    # change the divider depending on windows or posix
    dirvider = "/"
    if os.name == "nt":
        dirvider = "\\"

    if os.path.exists(f"{config_dir}{dirvider}servers.toml"):
        print("servers.toml exists!", file=sys.stderr)
    else:
        print(f"creating servers.toml in {config_dir}")
        create_servers_toml(config_dir)


if __name__ == "__main__":
    name = "python-sat"
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 and minor < 11:
        print(f"Error: You need python version >= 3.11 to use {
              name}.\n Currently on version {major}.{minor}", file=sys.stderr)
    install()
    system_install_unix(major, minor)
