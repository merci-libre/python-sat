#!/usr/bin/env python3
import os
import subprocess
import sys
import pathlib
import argparse


# build information

class BUILDINFO:
    version = "1.2"
    name = "sat"

# installation flags.


class INSTALLFLAGS:

    """
    Change these if you would like to change
    any of the installation settings.
    """
    # XDG compliant directory
    config_dir = 'default'
    # install to system.
    system_install = True


def parse_args():
    """
    parse user arguments from STDIN.
    """
    parser = argparse.ArgumentParser(
        usage='install.py [OPTIONS]')
    parser.add_argument("--uninstall", "-u",
                        default=False,
                        action="store_true",
                        help='''
                        Uninstall python-sat
                        ''')
    parser.add_argument("--system-install", "-i",
                        default=True,
                        action="store_true",
                        help='''
                        perform a system-install.
                        ''')
    return parser.parse_args()


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
                self.choice = 1
            case '2':
                self.choice = 2
            case 'q' | 'Q':
                exit(0)
            case _:
                print(f"{choice} unknown input, please try again",
                      file=sys.stderr)
                raise ValueError


class MacOS:
    def get_deps(self):
        import sys
        try:
            # assume all are missing...
            missingdeps = []
            with open("requirements.txt", 'r') as deps:
                for line in deps.readlines():
                    missingdeps.append(line.rstrip())
                deps.close()
            if missingdeps.__contains__(""):
                missingdeps.remove("")

            import build
            missingdeps.remove("build")

            import setuptools
            missingdeps.remove("setuptools")
            import icmplib
            missingdeps.remove("icmplib")
            import requests
            missingdeps.remove("requests")

            print("dependencies obtained!")
        except ModuleNotFoundError:
            try:
                for missingdep in missingdeps:
                    print()
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", missingdep])
            except Exception as e:
                print("Error: failed to install dependencies")
                print(e)
            print("dependencies obtained!")

    def system_uninstall():
        import sys
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "uninstall", "serveradmintool"])

    def system_install(self):
        MacOS().get_deps()
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "build"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "."])


class Linux():
    lib_path = ""
    bin_path = ""
    major = 0
    minor = 0
    command = "sudo"

    def __init__(self, major=None, minor=None):
        self.major = major
        self.minor = minor
        self.lib_path = f"/usr/lib/python{
            self.major}.{self.minor}/serveradmintool"
        self.bin_path = "/usr/local/bin"

    def get_packages(self):
        # determine package manager
        try:
            import icmplib
            import requests
        except ImportError:
            # default package manager
            package_manager_cmd = ""
            if os.path.exists("/usr/bin/zypper"):
                package_manager_cmd = "zypper"
            if os.path.exists("/usr/bin/apt-get"):
                package_manager_cmd = "apt-get"
            if os.path.exists("/usr/bin/pacman"):
                package_manager_cmd = "pacman"
            if os.path.exists("/usr/bin/yum"):
                package_manager_cmd = "yum"
            if os.path.exists("/usr/bin/dnf"):
                package_manager_cmd = "dnf"
            if os.path.exists("/usr/bin/emerge"):
                package_manager_cmd = "emerge"
            print("installing system packages...")

            match package_manager_cmd:
                case "emerge":
                    print("Gentoo is not supported (yet)!")
                    exit(1)
                case "dnf" | "yum":
                    print("Generic Linux is not supported!")
                    exit(1)
                case "zypper":
                    print("openSUSE is not supported!")
                    exit(1)
                case "pacman":
                    # refresh repo
                    subprocess.check_call(
                        [self.command, package_manager_cmd, "-Sy"])
                    # install packages
                    subprocess.check_call(
                        [self.command, package_manager_cmd, "-S", "python-icmplib", "python-requests"])
                case "apt-get":
                    # refresh repo
                    subprocess.check_call(
                        [self.command, package_manager_cmd, "update"])
                    # install packages
                    subprocess.check_call(
                        [self.command,
                         package_manager_cmd,
                         "install",
                         "python3-icmplib"])
                    subprocess.check_call(
                        [self.command,
                         package_manager_cmd,
                         "install",
                         "python3-requests"])

    def which_superuser(self):
        """
        Determines whether doas or sudo is run. Depending on which is installed
        """
        sudo = False
        doas = False

        command = "sudo"
        if os.path.exists("/usr/bin/sudo"):
            print("sudo detected...")
            command = "sudo"
            sudo = True
        if os.path.exists("/usr/bin/doas"):
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
                    choice = ReadOneChar().choice
                except ValueError:
                    continue
                match choice:
                    case 1:
                        command = "sudo"
                    case 2:
                        command = "doas"
                break
        sys.stderr.write(f"choice: {command} \n")
        return command

    def system_uninstall(self, command):
        lib_removed = False
        bins_removed = False

        if not os.path.exists(self.lib_path):
            lib_removed = True
            print("libraries are already uninstalled!")
        if not os.path.exists(f"{self.bin_path}/sat"):
            bins_removed = True
            print("binaries are uninstalled!")
        # handle uninstall
        match (bins_removed, lib_removed):
            case (True, True):
                # both uninstalled
                pass
            case (True, False):
                # libs still exist.
                print(f"running {command} rm -rv {self.lib_path}...")
                subprocess.check_call(
                    [command, "rm", "-rv", f"{self.lib_path}"])
            case (False, True):
                # bins still exist.
                print(f"running {command} rm -v {self.bin_path}/sat...")
                subprocess.check_call(
                    [command, "rm", "-v", f"{self.bin_path}/sat"])
            case (False, False):
                print(f"running {command} rm -v {self.bin_path}/sat...")
                subprocess.check_call(
                    [command, "rm", "-v", f"{self.bin_path}/sat"])
                print(f"running {command} rm -rv {self.lib_path}...")
                subprocess.check_call(
                    [command, "rm", "-rv", f"{self.lib_path}"])

    def system_install(self):
        """
        Installs the system packages via the install.sh
        script provided in the directory.

        Only allowed for POSIX based machines at the moment.
        """
        print("Starting system install for python-sat ")
        # do a system install for linux machines.
        if os.name == "posix" and INSTALLFLAGS.system_install:
            self.command = Linux(self.major, self.minor).which_superuser()
            Linux(self.major, self.minor).get_packages()

            print(f"installing libraries to {self.lib_path}")
            print(f"installing sat to {self.bin_path}")

            print(f"checking if {self.lib_path} exists...")
            if os.path.exists(self.lib_path):
                print(f"{self.lib_path} already exists!")
                uninstall = False
                while True:
                    print("\nsat is already installed on your machine!")
                    print("Would you like to uninstall or reinstall it?")

                    print("\n Files to remove:")
                    print(f"libraries- {self.lib_path}")
                    print(f"binaries- {self.bin_path}/sat")

                    print("[1] remove")
                    print("[2] reinstall")
                    print("[q]uit\n")
                    try:
                        choice = ReadOneChar().choice
                    except ValueError:
                        continue
                    match choice:
                        case 1:
                            choice = "remove"
                            uninstall = True
                        case 2:
                            choice = "reinstall"
                            uninstall = False
                    break

                sys.stderr.write(f"choice: {choice} \n")
                self.system_uninstall(self.command)
                if uninstall:
                    print("\npython-sat was uninstalled!")
                    exit(0)

            print(
                f"running {self.command} ./install.sh {self.bin_path} {self.lib_path}")
            subprocess.check_call(
                [self.command, "./install.sh", self.bin_path, self.lib_path])


def make_config():
    """
    although it says linux/windows, it is system agnostic
    """
    POSIX = (os.name == "posix")
    DARWIN = (sys.platform == "darwin")
    WINDOWS = (os.name == "nt")
    homedir = f"{pathlib.Path.home()}"
    configuration = ""

    if POSIX or DARWIN:
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

    if homedir == "" or configuration == "":
        raise Exception
    path_to_config = f"{homedir}{configuration}"

    return path_to_config


def install(major: int, minor: int, name: str, version: str):
    """
    installs the program.
    """

    print(f"installing {name}{version} for {sys.platform} machines")

    # no windows!!!
    if os.name == "nt":
        print("someone did not read the readme...")
        print("Install WSL for windows, and use debian or",
              "\nubuntu linux for python-sat!")
        print("https://learn.microsoft.com/en-us/windows/wsl/install")
        print("\nFor the easiest to use, get Ubuntu Linux for WSL.")
        exit(1)

    if INSTALLFLAGS.system_install and sys.platform == "linux":
        Linux(major, minor).system_install()

    # install for macOS
    if INSTALLFLAGS.system_install and sys.platform == "darwin":
        MacOS().system_install()

    config_dir = make_config()

    try:
        os.makedirs(config_dir)
        print(f"created configuration directory @ {config_dir}")
    except FileExistsError:
        pass

    # change the divider depending on windows or posix
    dirvider = "/"

    if not os.path.exists(f"{config_dir}{dirvider}servers.toml"):
        print(f"creating servers.toml in {config_dir}")
        create_servers_toml(config_dir)


if __name__ == "__main__":
    major = sys.version_info.major
    minor = sys.version_info.minor
    args = parse_args()
    INSTALLFLAGS.system_install = args.system_install

    if major < 3 and minor < 11:
        print(f"Error: You need python version >= 3.11 to use {
              BUILDINFO.name}.\n Currently on version {major}.{minor}", file=sys.stderr)
        exit(1)

    if args.uninstall:
        print(f"Uninstalling {BUILDINFO.name}...")
        try:
            if sys.platform == "darwin":
                MacOS().system_uninstall()
            if sys.platform == "linux":
                command = Linux(major, minor).which_superuser()
                Linux(major, minor).system_uninstall(command)
        except Exception as e:
            print("Error failed to uninstall sat.", file=sys.stderr)
            print(f"{e}", file=sys.stderr)

        exit(0)
    # install
    try:
        install(major, minor, BUILDINFO.name, BUILDINFO.version)
    except Exception as e:
        print(f"failed to install {BUILDINFO.name} {
              BUILDINFO.version}", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
