#!/usr/bin/env python3
import pip
import os
import sys

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
    homedir = ""
    configuration = ""

    if LINUX:
        homedir = os.path.expanduser('~')
        if INSTALLFLAGS.config_dir == "default":
            configuration = "/.config/server_admin_tool/"
        else:
            configuration = INSTALLFLAGS.config_dir

    if WINDOWS:
        homedir = os.path.expanduser("~home")
        if INSTALLFLAGS.config_dir == "default":
            configuration = "\\Documents\\server_admin_tool\\"
        else:
            configuration = INSTALLFLAGS.config_dir

    if homedir == "" or configuration == "":
        raise Exception
    path_to_config = f"{homedir}{configuration}"

    return path_to_config


def resolve_dependencies(dependencies: list):
    pipargs = ["install"]
    getdeps = False
    for i in dependencies:
        pipargs.append(i)
    try:
        if pip.main(pipargs) == 0:
            print("dependencies installed!")
            getdeps = True
    except pip._internal.exceptions.ExternallyManagedEnvironment:
        print("We are in a ExternallyManagedEnvironment, install with venv.")
    except Exception as e:
        print(f"Could not resolve dependencies, or pip failed:\n {e}")
    return getdeps


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
    lib_path = f"/usr/lib/python{major}.{
        minor}/site-packages/serveradmintool"
    bin_path = "/usr/local/bin"
    """
    Installs the system packages via the install.sh
    script provided in the directory.

    Only allowed for POSIX based machines at the moment.
    """
    # do a system install for linux machines.
    if os.name == "posix" and INSTALLFLAGS.system_install:
        sudo = False
        doas = False
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
        getdeps = True
    except ImportError:
        print("installing dependencies...")
        getdeps = resolve_dependencies(dependencies)

    if not getdeps:
        print("failed to install dependencies")
        exit(1)

    config_dir = make_config()
    try:
        os.makedirs(config_dir)
        print(f"created configuration directory @ {config_dir}")
    except FileExistsError:
        pass
    if os.path.exists(f"{config_dir}/servers.toml"):
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
