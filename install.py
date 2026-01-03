#!/usr/bin/env python3
import os
import time
import subprocess
import sys
import pathlib
import argparse


# =========== argument parser ============= #
def parse_args():
    """
    parse user arguments from STDIN.
    """
    parser = argparse.ArgumentParser(
        usage='install.py [OPTIONS]')
    parser.add_argument("--force-reinstall", "-F",
                        default=False,
                        action="store_true",
                        help='''
                        Force re-build and re-install python-sat.
                        ''')
    parser.add_argument("--uninstall", "-u",
                        default=False,
                        action="store_true",
                        help='''
                        Uninstall python-sat
                        ''')
    parser.add_argument("--update",
                        default=False,
                        action="store_true",
                        help='''
                        Updates the package to the latest git version using
                        `git pull`, and forces a reinstall.
                        REQUIRES `git` to be installed!
                        ''')
    return parser.parse_args()


# build information
class BUILDINFO:
    version = "2.0p2 (2.0.2)"
    name = "sat"


# installation flags.
class INSTALLFLAGS:

    """
    Change these if you would like to change
    any of the installation settings.
    """
    # Default is set to the default xdg-compliant
    # directory.
    config_dir = 'default'
    # install to system.
    system_install: bool
    force_reinstall: bool


# Read 1 char from STDIN
class ReadOneChar:
    """
    Gets a single character for input.
    Used for prompting the user throughout
    the install script.
    """

    def __init__(self):
        import tty
        import sys
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        # get raw stdin from the user.
        try:
            tty.setraw(sys.stdin.fileno())
            choice = sys.stdin.read(1)

        # reset the terminal
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # get the choice by the user, q will always exit.
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


# ============ macOS Installation =========
class MacOS:
    """
    Installation process for MacOS. Uses pip for all of the installation
    process, as well as all of the tools required to build the project.
    """

    def get_deps(self):
        """
        Gets the dependencies for MacOS,
        each dependencies that are already
        existing on the system get removed from
        the missingdeps list-- as soon as a missing
        dependency is found, it will install any remaining
        that are missing.
        """
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
        """
        Uninstalls python-sat from the machine :(
        """
        import sys
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "uninstall", "serveradmintool"])

    def system_install(self):
        """
        Installs via pip.
        """
        MacOS().get_deps()
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "build"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "."])


# ============================= Linux Installation =========
class Linux():
    """
    All of the installation tools for Unix/Linux
    based systems. Uses system packages, and gets
    the main dependencies from whatever system package
    manager it detects.

    BSD based systems yet to be implemented or supported :(
    """
    old_lib_path = ""
    old_bin_path = ""
    major = 0
    minor = 0
    command = "sudo"

    def __init__(self, major=None, minor=None):
        self.major = major
        self.minor = minor

    def get_packages(self, command):
        """
        Get the packages for building and running from
        the system package manager. Supports Debian and
        Arch based systems currently, but as soon as I
        test on other distributions, they will be added here.
        """
        # determine package manager
        try:
            import icmplib
            import requests
            import build
            import setuptools
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
                    # sync repositories
                    subprocess.check_call(
                        [self.command, package_manager_cmd, "-Sy"])
                    # install packages
                    subprocess.check_call(
                        [self.command,
                         package_manager_cmd,
                         "-S",
                         "python-build",
                         "python-setuptools",
                         "python-icmplib",
                         "python-requests"])
                case "apt-get":
                    # sync repositories
                    subprocess.check_call(
                        [self.command, package_manager_cmd, "update"])
                    # install packages
                    subprocess.check_call(
                        [self.command,
                         package_manager_cmd,
                         "install",
                         "python3-icmplib",
                         "python3-requests",
                         "python3-setuptools",
                         "python3-build"])

    def which_superuser(self):
        """
        Determines whether doas or sudo is run privileged commands.
        Depending on which is installed. If both are installed, the
        user will be prompted via stdin to pick one.
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

        # if both sudo and doas are detected, prompt for one.
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

    def old_system_uninstall(self, command):
        """
        Old system uninstall is here for users who installed
        via the install script prior to versions 1.3+, where
        manual binaries and libraries were created.

        On installation, it should create the package via pip
        and install it through pip. This allows the user to
        manage packages more efficiently, as well as use the
        package as intended.

        Prior to version <1.3, sat/sat.py was moved to the /usr/local/bin
        directory, and it would not run the package as intended. In
        order to avoid this from occuring, I switched Linux installations
        to use pip, which is not only more efficient-- but more orthodox.
        """
        lib_removed = False
        bins_removed = False

        if not os.path.exists(self.old_lib_path):
            lib_removed = True
            print("libraries are already uninstalled!")
        if not os.path.exists(f"{self.old_bin_path}/sat"):
            bins_removed = True
            print("binaries are uninstalled!")
        # handle uninstall
        match (bins_removed, lib_removed):
            case (True, True):
                # both uninstalled
                pass
            case (True, False):
                # libs still exist.
                print(f"running {command} rm -rv {self.old_lib_path}...")
                subprocess.check_call(
                    [command, "rm", "-rv", f"{self.old_lib_path}"])
            case (False, True):
                # bins still exist.
                print(f"running {command} rm -v {self.old_bin_path}/sat...")
                subprocess.check_call(
                    [command, "rm", "-v", f"{self.old_bin_path}/sat"])
            case (False, False):
                print(f"running {command} rm -v {self.old_bin_path}/sat...")
                subprocess.check_call(
                    [command, "rm", "-v", f"{self.old_bin_path}/sat"])
                print(f"running {command} rm -rv {self.old_lib_path}...")
                subprocess.check_call(
                    [command, "rm", "-rv", f"{self.old_lib_path}"])

    def full_install(self, command):
        """
        Performs a full system install.
        Builds the project from source,
        using build, setuptools, and pip.
        """
        print("building the packages...")
        try:
            user = os.getlogin()
            subprocess.check_call([sys.executable, "-m", "build"])
            subprocess.check_call(
                [command,
                 sys.executable,
                 "-m",
                 "pip",
                 "install",
                 "--root-user-action",
                 "ignore",
                 "--break-system-packages",
                 "."])
            subprocess.check_call(
                [command,
                 "chown",
                 "-R",
                 f"{user}:{user}",
                 "build"]
            )
        except subprocess.SubprocessError:
            raise Exception("Failed to install packages from install.")

    def system_uninstall(self, command):
        """
        Uninstalls python-sat with pip.
        """
        subprocess.check_call(
            [command, sys.executable, "-m",
             "pip",
             "uninstall",
             "--root-user-action",
             "ignore",
             "--break-system-packages",
             "serveradmintool"])

    def system_install(self):
        """
        Installs the system packages via the install.sh
        script provided in the directory.

        Only allowed for POSIX based machines at the moment.
        """

        self.old_lib_path = f"/usr/lib/python{self.major}.{
            self.minor}/site-packages/serveradmintool"
        self.old_bin_path = "/usr/local/bin"

        # detects the old installation directories.
        old_install = (os.path.exists(self.old_lib_path) or os.path.exists(
            f"{self.old_bin_path}/sat"))

        # do a system install for linux machines.
        print("Starting system install for python-sat ")
        if os.name == "posix" and INSTALLFLAGS.system_install:
            self.command = Linux(self.major, self.minor).which_superuser()
            Linux(self.major, self.minor).get_packages(self.command)

            # remove old installation method, we use pip now.
            print(f"checking if {self.old_lib_path} exists...")

            # uninstalls the old code written.
            if old_install:
                print(f"{self.old_lib_path} exists!")
                print("As of python-sat 1.3",
                      "system installs use pip to install the package")

                print("\n Files to remove:")
                print(f"libraries= {self.old_lib_path}")
                print(f"binaries= {self.old_bin_path}/sat")

                self.old_system_uninstall(self.command)

        try:

            print("checking if python-sat already exists...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "show", "serveradmintool"],
                stdout=subprocess.DEVNULL)
            # force reinstall
            if INSTALLFLAGS.force_reinstall:
                Linux().full_install(self.command)
                exit(0)

            print("\npython-sat was already installed!",
                  "(pip show serveradmintool)")
            print("To force rebuild and reinstall, run this again with -F")
            print("To uninstall, run this again with the --uninstall argument")
            exit(1)
        except subprocess.SubprocessError:
            # catches if pip show fails.
            print("building the packages...")
            Linux().full_install(self.command)


# ========== servers.toml and configuration ============== #
def create_servers_toml(config_dir: str):
    """
    Creates the initial servers toml
    on installation.
    """
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

    print(f"{config_dir}servers.toml was created.")


def make_config():
    """
    Makes the configuration directory for the user.
    """
    POSIX = (os.name == "posix")
    DARWIN = (sys.platform == "darwin")
    WINDOWS = (os.name == "nt")  # not supported!
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
        print("Windows installs are not supported.")
        exit(1)

    if homedir == "" or configuration == "":
        raise Exception
    path_to_config = f"{homedir}{configuration}"

    return path_to_config


def install(major: int, minor: int, name: str, version: str):
    """
    installs the program.
    """

    print(f"installing {name} {version} for {sys.platform} machines")

    # no windows!!!
    if os.name == "nt":
        print("someone did not read the readme...")
        print("Install WSL for windows, and use debian or",
              "\nubuntu linux for python-sat!")
        print("https://learn.microsoft.com/en-us/windows/wsl/install")
        print("\nFor the easiest to use, get Ubuntu Linux for WSL.")
        exit(1)

    # installation for linux machines.
    if INSTALLFLAGS.system_install and sys.platform == "linux":
        Linux(major, minor).system_install()

    # install for macOS
    if INSTALLFLAGS.system_install and sys.platform == "darwin":
        MacOS().system_install()

    config_dir = make_config()

    # make the configuration directory.
    try:
        print(f"created configuration directory @ {config_dir}")
        os.makedirs(config_dir)
    except FileExistsError:
        pass

    # change the divider depending on windows or posix
    dirvider = "/"

    # create the toml file.
    if not os.path.exists(f"{config_dir}{dirvider}servers.toml"):
        print(f"creating servers.toml in {config_dir}")
        create_servers_toml(config_dir)


def main():
    major = sys.version_info.major
    minor = sys.version_info.minor
    # parse user arguments.
    args = parse_args()
    INSTALLFLAGS.system_install = not args.uninstall
    INSTALLFLAGS.force_reinstall = args.force_reinstall

    # if the user doesn't have 3.11+, exit with an error message.
    if major < 3 and minor < 11:
        print(f"Error: You need python version >= 3.11 to use {
              BUILDINFO.name}.\n Currently on version {major}.{minor}", file=sys.stderr)
        exit(1)

    # uninstallation script.
    if args.uninstall:
        print(f"Uninstalling {BUILDINFO.name}...")
        try:
            if sys.platform == "darwin":
                MacOS().system_uninstall()
            if sys.platform == "linux":
                command = Linux(major, minor).which_superuser()
                print(f"uninstalling with {command} {
                      sys.executable} -m pip...")
                Linux(major, minor).system_uninstall(command)
        except Exception as e:
            print("Error failed to uninstall sat.", file=sys.stderr)
            print(f"{e}", file=sys.stderr)

        exit(0)
    if args.update:
        try:
            subprocess.check_call(("git", "pull"))
            print(f"{BUILDINFO.name} up to date!")
            time.sleep(1)
            # when installing, the build info is incorrect.
            INSTALLFLAGS.force_reinstall = True
        except Exception as e:
            print(f"failed to update {BUILDINFO.name} {
                BUILDINFO.version}", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)

    # installation script.
    try:
        install(major, minor, BUILDINFO.name, BUILDINFO.version)
    except Exception as e:
        print(f"failed to install {BUILDINFO.name} {
              BUILDINFO.version}", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled installation script...")
        exit(0)
    except EOFError:
        print("\nCancelled installation script...")
        exit(0)
