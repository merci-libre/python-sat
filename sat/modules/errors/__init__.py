"""
This module is responsible for creating customized
errors within python-sat.
"""
import sys
from threading import Thread
import traceback
try:
    import sat.modules.ansi as ansi
except ModuleNotFoundError:
    import modules.ansi as ansi


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Check():
    """
    Used in the __create_threads function to check the values of the data.
    Also maybe used in externally to validate the values of parsed toml data.
    Moved here to reduce lines in main.
    """

    def scan(self, scan, server_id):
        scan_error = ConnectivityDefinitions.Scan
        match scan:
            case bool():
                return scan
            case _:
                raise scan_error.IncorrectType(server_id)

    def ports(self, ports, server_id) -> bool:
        """
        Checks the values of the ports, if any return an
        error, deal with outside of this method.
        """
        MIN_PORT = 1
        MAX_PORT = 65535

        port_errors = ConnectivityDefinitions.Ports

        match ports:
            case list():
                # checks if all in port list are integers.
                # if all is well, sort the list.
                ports_all_ints = all(isinstance(port, int) for port in ports)

                if not ports_all_ints:
                    raise port_errors.IncorrectType(server_id)

                # we also need to drop duplicate values, so we have to convert
                # the list into a dictionary and back into a list.

                ports = list(dict.fromkeys(ports))
                ports.sort()

                # check the values to ensure all are within valid ports
                all_valid = all(MIN_PORT <= port <= MAX_PORT for port in ports)

                if not all_valid:
                    raise port_errors.PortOutOfRange(server_id)
                return ports

            case int():
                # since we are iterating over this reduces overhead
                port_to_list = []
                if ports <= 0 or MAX_PORT < ports:
                    raise port_errors.PortOutOfRange(server_id)
                port_to_list.append(ports)
                return port_to_list
            # if neither matches...
            case None:
                pass
            case _:
                raise port_errors.IncorrectType(server_id)

    def ip(self, ip, server_id):
        """
        checks the ip
        """
        ip_errors = ConnectivityDefinitions.IPAddressErrors(server_id)
        match ip:
            case str():
                if ip == "":
                    raise ip_errors.BadIPAddressValue(server_id)
            case _:
                raise ip_errors.IncorrectType(server_id)
        return ip


class Main(Exception):
    """
    All of these errors deal with the main thread.
    This can return anything from a panic, to an import error.
    All errors in this class are fatal.

    Code 1-50 are all related to main.
    """
    class ImportError(Exception):

        def __str__(self):
            return f"FATAL: {self.message}\n{ansi.RED}{self.traceback}{ansi.END}\n{self.traceback}"

        def __init__(self,
                     message="Failed to import the libraries within main...",
                     code=1):
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)


class Connection(Exception):
    """
    These errors are raised when a user a connection inside of
    the connectivity module are raised, we raise these when connectivity
    fails to either run properly, or when there is an issue with ICMPlib
    in particular.

    Codes 50-100 relate to this class.
    """
    class Privileges(Exception):
        """
        This is the same as icmplib.exceptions.SocketpermissionError
        (see:)
        (https://github.com/ValentinBELYN/icmplib/blob/main/icmplib/exceptions.py)
        However, we implement a custom message rather than just the original.
        """

        def __str__(self):
            return f"{ansi.RED}{self.message}:{ansi.END}\n{self.traceback}"

        def __init__(self,
                     message="You need to run this command as root!",
                     code=1001):
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)


class Threads(Exception):
    """
    These errors are all related to issues with the threading
    module.

    Including but not limited to:

    Failing to join, failing to load the data, or failing to
    run.

    Code 1000's are ALL related to thread issues
    """
    class FailedToCreate(Exception):
        """
        Raised when the user cannot generate the thread in main.
        Considered a non-fatal error.
        """

        def __str__(self):
            return f"{self.thread}: {self.message}\n{ansi.RED}{
                self.traceback}{ansi.END}"

        def __init__(self, thread: Thread,
                     message="Thread failed to create.",
                     code=1001):
            self.thread = thread
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)

    class FailedToJoin(Exception):
        """
        Raised when the thread process CANNOT join the main thread after
        timeout, or the thread for whatever reason fails to join to main.

        This is considered a fatal error.
        """

        def __str__(self):
            return f"{self.thread}: {self.message}\n{ansi.RED}{
                self.traceback}{ansi.END}"

        def __init__(self, thread: Thread,
                     message="Thread failed to join to MainThread!",
                     code=1002):
            self.thread = thread
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)

    class FailedToRun(Exception):
        """
        Raised when the thread process CANNOT start the process of
        creating a fork of the main process.

        This CAN be considered a fatal error, however-- I have yet
        to encounter this issue.
        """

        def __str__(self):
            return f"{self.thread}: {self.message}\n{ansi.RED}{
                self.traceback}{ansi.END}"

        def __init__(self, thread,
                     message="Thread failed to run.",
                     code=1003):
            self.thread = thread
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)


class TomlFiles(Exception):
    """
    These errors are all related to TOML file parsing.
    Including but not limited to:

    Read/Write permissions, Missing Files, etc.
    Codes 2000's are ALL related to toml files
    """

    class Permissions:
        # These handle r/w permissions.
        class ReadPermissions(Exception):
            """
            Raised when the user lacks read permissions to the file.
            """

            def __str__(self):
                return f"{self.path}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self,
                         path: str,
                         message="lacking write or read permissions to path.",
                         code=2001):
                self.path = path
                self.message = message
                self.code = code
                self.traceback = traceback.format_exc()
                super().__init__(message)

        class WritePermissions(Exception):
            """
            Raised when the user lacks write permissions to the file.
            """

            def __str__(self):
                return f"{self.path}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self,
                         path: str,
                         message="lacking write permissions to file path.",
                         code=2002):
                self.path = path
                self.message = message
                self.code = code
                self.traceback = traceback.format_exc()
                super().__init__(message)

    class TomlFileMissing(Exception):
        def __str__(self):
            return f"{self.file}: {self.message}\n{ansi.RED}{
                self.traceback}{ansi.END}"

        def __init__(self, file: str, message="file is missing", code=2003):
            self.file = file
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)

    class DeserializationFailure(Exception):
        """
        Raised when the file parsed is either not a toml file,
        or it is incorrectly structured.
        """

        def __str__(self):
            return f"{self.file}: {self.message}\n{ansi.RED}{
                self.traceback}{ansi.END}"

        def __init__(self, file: str, message="is not a toml file", code=2004):
            self.file = file
            self.message = message
            self.code = code
            self.traceback = traceback.format_exc()
            super().__init__(message)


class ConnectivityDefinitions(Exception):

    class IPAddressErrors(Exception):

        class BadIPAddressValue(Exception):
            def __str__(self):
                return f"{self.server_name}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self,
                         server_name,
                         message="`ip` value is empty or null.",
                         code=3001):

                self.server_name = server_name
                self.message = message
                self.code = code
                self.traceback = traceback.format_exc()
                super().__init__(message)

        class IncorrectType(Exception):
            def __str__(self):
                return f"{self.server_name}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self,
                         server_name,
                         message="`ip` must be a str()",
                         code=3002):

                self.server_name = server_name
                self.message = message
                self.code = code
                super().__init__(message)

    class Ports(Exception):
        class PortOutOfRange(Exception):
            def __str__(self):
                return f"{self.server_name}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self, server_name,
                         message="port(s) must be in the range(1, 65535)",
                         code=3003):
                self.server_name = server_name
                self.message = message
                self.code = code
                self.traceback = traceback.format_exc()
                super().__init__(message)

        class IncorrectType(Exception):

            def __str__(self):
                return f"{self.server_name}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self, server_name,
                         message="port(s) must be type 'int' or list[int]",
                         code=3004):
                self.server_name = server_name
                self.message = message
                self.code = code
                self.traceback = traceback.format_exc()
                super().__init__(message)

    class Scan(Exception):
        class IncorrectType(Exception):
            def __str__(self):
                return f"{self.server_name}: {self.message}\n{ansi.RED}{
                    self.traceback}{ansi.END}"

            def __init__(self, server_name,
                         message="Scan value must be a boolean",
                         code=3005):
                self.server_name = server_name
                self.message = message
                self.code = code
                self.traceback = traceback.format_exc()
                super().__init__(message)
