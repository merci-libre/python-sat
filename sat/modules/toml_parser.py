import os
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
    homedir = ""
    configuration = ""

    if LINUX:
        homedir = os.path.expanduser('~')
        configuration = "/.config/server_admin_tool/"

    if WINDOWS:
        homedir = os.path.expanduser("~home")
        configuration = "\\Documents\\server_admin_tool\\"

    path_to_config = f"{homedir}{configuration}servers.toml"
    if homedir == "" or configuration == "":
        raise errors.TomlFiles.TomlFileMissing(path_to_config)

    del configuration, homedir
    return path_to_config


# not implemented yet
def write_toml(filename: str, server_count=5):
    """
    Used to create a custom list that the user can
    edit and define.
    """
    # argument parsing
    if filename.__contains__(".toml"):
        filename.replace(".toml", "")

    # actual writing
    with open(f"{filename}.toml", 'w') as toml:
        try:
            # top header
            toml.write("[servers]\n")
            for i in range(server_count):
                toml.write("\n[servers.{server_name}]")
                toml.write(
                    '\n\tip = # enter an IP address here, type="string"')
                toml.write(
                    '\n\tports = # enter a list i.e: [22, 1337, 65535]'
                )
                toml.write('\n\tscan= # enter a boolean value here')
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
