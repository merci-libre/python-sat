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
    print(f"installing sat for {os.name}")
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

    print(f"creating configuration directory @ {path_to_config}")
    return path_to_config


def resolve_dependencies(dependencies: list):
    pipargs = ["install"]
    for i in dependencies:
        pipargs.append(i)
    try:
        if pip.main(pipargs) == 0:
            print("dependencies installed!")
            return True
    except Exception as e:
        print(f"Could not resolve dependencies, or pip failed:\n {e}")
        return False
    return False


def install():
    dependencies = ["icmplib", "requests"]
    """
    installs the program.
    """
    # get dependencies

    try:
        import icmplib
        import requests
        getdeps = True
    except ImportError:
        print("installing dependencies...")
        getdeps = resolve_dependencies(dependencies)

    if not getdeps:
        print("failed to install dependencies!!!")
        exit(1)

    config_dir = make_config()
    try:
        os.makedirs(config_dir)
    except FileExistsError:
        pass
    create_servers_toml(config_dir)


if __name__ == "__main__":
    install()
