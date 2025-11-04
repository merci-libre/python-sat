try:
    from . import errors
    from . import ansi
except:
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


def write_toml(filename: str, out_data: dict):
    """
    Writes our tomlfile
    """
    pass


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
