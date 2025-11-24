import os
import pathlib
try:
    from . import errors
    from . import ansi
except ImportError:
    import ansi
    import errors
try:
    import tomllib
except ImportError:
    errors.eprint(
        f"{ansi.RED} [ ERROR ]: SAT requires python version >= 3.11.{
            ansi.END}",
        "\nExited with code 1")
    exit(1)

"""
This module is required to parse user's server.toml files
By default, it searches through the user's defined configuration folder.

Below are the default locations of the users .toml file that are built when
running install.py

# For Windows:
C:\\Documents\\server_admin_tool\\servers.toml

# For Linux/MacOS
$HOME/.config/server_admin_tool/servers.toml

You can also invoke the option -f to use another .toml file, so long that
the format of the file matches that of the one designated in the official
documentation. In addition, you can also invoke the -N option to create a
preformatted .toml file that you can manually edit.
"""


def get_toml_path() -> str:
    """
    determines the location of the toml file
    depending if the user is on linux or windows.

    For linux/unix/macOS users it checks the
    XDG compliant directory for the file, if it can't
    find the file, it raises an exception.
    """
    LINUX = (os.name == "posix")
    WINDOWS = (os.name == "nt")
    homedir = f"{pathlib.Path.home()}"
    configuration = ""

    if LINUX:
        configuration = "/.config/server_admin_tool/"

    if WINDOWS:
        configuration = "\\Documents\\server_admin_tool\\"

    path_to_config = f"{homedir}{configuration}servers.toml"
    if homedir == "" or configuration == "":
        raise errors.TomlFiles.TomlFileMissing(path_to_config)

    del configuration, homedir
    return path_to_config


def write_toml(filename: str, server_count=5):
    """
    Used to create a custom list that the user can
    edit and define. Overwrites the file if it is
    existing.
    """
    # removes a pre-emptive toml from the name, as
    # we already add this when writing.
    if filename.__contains__(".toml"):
        filename = filename.replace(".toml", "")

    with open(f"{filename}.toml", 'w') as toml:
        try:
            # top header
            toml.write("[servers]\n")
            # gives the user an example
            toml.write('\n# [server.{your_name_here}]\n')
            toml.write('\n# ip = "hostname/url/ip address": type=string\n')
            toml.write('\n# ports = [22,8080,443] : accepts list types\n')
            toml.write('\n# scan = type=boolean values (true or false)\n')

            toml.write('\n# for more details, please consult the',
                       'readme for more information.\n')
            for i in range(server_count):
                toml.write("\n[servers.{server_name}]")
                toml.write(
                    '\n\tip = ""')
                toml.write(
                    '\n\tports = []'
                )
                toml.write('\n\tscan=false')
                toml.write('\n')
        except FileExistsError:
            errors.eprint(f"{filename} already exists!")
            exit(1)
        except PermissionError:
            raise errors.TomlFiles.Permissions.WritePermissions(
                f"{filename}")
    del filename


def parse_toml(tomlfile: str) -> dict:
    """
    Reads toml file and deserializes the data.
    """
    try:
        with open(tomlfile, 'rb') as f:
            toml_data: dict = tomllib.load(f)
            return toml_data
    except FileNotFoundError:
        raise errors.TomlFiles.TomlFileMissing(tomlfile)
    except PermissionError:
        raise errors.TomlFiles.TomlReadPermissions(tomlfile)
    except tomllib.TOMLDecodeError:
        raise errors.TomlFiles.DeserializationFailure(tomlfile)
