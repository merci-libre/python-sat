"""
This module/library is responsible for keeping a log of
the program. Also contains the function used for the verbosity
argument
"""

import datetime
import sys
# system import
try:
    from . import ansi
    from .errors import eprint
except ImportError:
    import ansi
    from errors import eprint


class __globals:
    lines_written = 0


def __init__():
    __globals.lines_written += 1


class NoColor:
    log = {}
    log_errors = {}


class Color:
    log = {}
    log_errors = {}


class logging:
    id = 0
    error_id = 0


def error(*args):
    """
    Write an error message to the log, and to an
    errors section within the log file.
    """
    color = ansi.RED
    weight = ansi.BOLD

    time = datetime.datetime.now()
    logging.id += 1
    logging.error_id += 1
    message = str()
    for message_str in args:
        message += message_str

    # information
    log_info = f"[id={logging.id}::{time}]"
    log_type = "[ERROR]"

    # coloring
    uncolored = f"{log_info}{log_type}{message}"
    colored_message = f"{log_info}{color}{log_type}{ansi.END}: {message}"

    # write to logs.
    Color.log[logging.id] = colored_message
    NoColor.log[logging.id] = uncolored

    # write to separate logs.
    log_info = f"[id={logging.id};eid={logging.error_id}::{time}]"
    uncolored = f"{log_info}{log_type}{message}"
    colored_message = f"{log_info}{color}{log_type}{ansi.END}: {message}"
    del message, time
    Color.log_errors[(logging.error_id, logging.id)] = colored_message
    NoColor.log_errors[(logging.error_id, logging.id)] = uncolored


def start(*args):
    time = datetime.datetime.now()
    """
    Write a start message to the log
    """
    color = ansi.BLUE
    logging.id += 1

    message = str()
    for message_str in args:
        message += message_str

    # information
    log_info = f"[id={logging.id}::{time}]"
    log_type = "(START):"

    # coloring
    uncolored = f"{log_info}{log_type}{message}"
    colored_message = f"{log_info}{ansi.BOLD}{
        color}{log_type}{message}{ansi.END}"

    del message, time
    # write to logs.
    Color.log[logging.id] = colored_message
    NoColor.log[logging.id] = uncolored


def notify(*args):
    time = datetime.datetime.now()
    """
    Write a notification based message to the log
    """
    color = ansi.YELLOW
    logging.id += 1

    message = str()
    for message_str in args:
        message += message_str

    # information
    log_info = f"[id={logging.id}::{time}]"
    log_type = "[NOTICE]"

    # coloring
    uncolored = f"{log_info}{log_type} {message}"
    colored_message = f"{log_info}{ansi.BOLD}{
        color}{log_type}{message}{ansi.END}"

    del message, time
    # write to logs.
    Color.log[logging.id] = colored_message
    NoColor.log[logging.id] = uncolored


def info(*args):
    time = datetime.datetime.now()
    """
    Write information on values to the log
    """
    color = ansi.LIGHT_BLUE

    logging.id += 1
    message = str()
    for message_str in args:
        message += message_str

    # information
    log_info = f"[id={logging.id}::{time}]"
    log_type = "(info)"

    # coloring
    uncolored = f"{log_info}{log_type} {message}"
    colored_message = f"{log_info}{color}{log_type} {message}{ansi.END}"

    del message, time
    # write to logs.
    Color.log[logging.id] = colored_message
    NoColor.log[logging.id] = uncolored


def write(*args):
    time = datetime.datetime.now()
    """
    Write a standard message to the log
    """
    color = ansi.GREEN

    logging.id += 1
    message = str()
    for message_str in args:
        message += message_str

    # information
    log_info = f"[id={logging.id}::{time}]"
    log_type = "(OK)"

    # coloring
    uncolored = f"{log_info}{log_type}{message}"
    colored_message = f"{log_info}{color}{log_type} {message}{ansi.END}"

    del message, time
    # write to logs.
    Color.log[logging.id] = colored_message
    NoColor.log[logging.id] = uncolored


def __clear_log():
    for i in range(__globals.lines_written):
        sys.stderr.write('\x1b[1A')
        sys.stderr.write('\x1b[2K')

    __globals.lines_written = 0


def print_log(clear=False, initial=False):
    if clear and not initial:
        __clear_log()
    for id in Color.log.keys():
        eprint(f"{Color.log.get(id)}",)
    # print the errors
    eprint("\n\nErrors that occurred:")
    for (error_id, id) in Color.log_errors.keys():
        eprint(f"{Color.log_errors.get((error_id, id))}")


def write_log():
    """
    Write the log out to a file. Creates the logfile:
    `sat-{CURRENT_UNIX_TIME_STAMP}.log`
    will create in /tmp/directory.
    """
    unix_timestamp = str(datetime.datetime.utcnow()).replace(" ", "_").replace(
        ":", "-")
    # format the unix_timestamp to fit naming convention.

    # set the userid so that root does not own the file.
    with open(f"/tmp/sat_log{unix_timestamp}.log", "w") as logfile:
        # write out the main log.
        for id in NoColor.log.keys():
            logfile.write(f"{NoColor.log.get(id)}\n")

        # write the errors.
        for (error_id, id) in NoColor.log_errors.keys():
            logfile.write(
                f"{NoColor.log_errors.get(error_id, id)}")
    logfile.close()
    eprint(f"logfile written to {logfile}")


if __name__ == "__main__":
    write("hello", "world", "no")
    notify("[THIS IS A NOTIFICATION]", '\n\tdo something')
    error("this", "\nis an ", "error")
    write("hello", "world", "no")
    notify("[THIS IS A NOTIFICATION]", '\n\tdo something')
    error("this", "\nis an ", "error")
    print_log()
