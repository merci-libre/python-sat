"""
This module/library is responsible for keeping a log of
the program. Also contains the function used for the verbosity
argument
"""

import datetime
# system import
try:
    from . import ansi
except ImportError:
    import ansi
log_wrapped = {}
log_no_color = {}
log_errors = {}


class log:
    id = 0
    error_id = 0


def error(*args):
    """
    Write an error message to the log, and to an
    errors section within the log file.
    """
    log.id += 1
    log.error_id += 1
    message = str()
    for message_str in args:
        message += message_str

    fmessage = f"[ERROR]: {message}{ansi.END}"
    colored_message = f"{ansi.RED}{ansi.UNDERLINE}{fmessage}"

    log_wrapped[log.id] = colored_message
    log_errors[(log.error_id, log.id)] = fmessage
    log_no_color[log.id] = fmessage


def notify(*args):
    """
    Write a notification based message to the log
    """
    log.id += 1

    message = str()
    for message_str in args:
        message += message_str

    fmessage = f"[NOTICE] {message}"
    colored_message = f"{ansi.YELLOW}{fmessage}"

    # write to logs.
    log_wrapped[log.id] = colored_message
    log_no_color[log.id] = fmessage


def write(*args):
    """
    Write a standard message to the log
    """

    log.id += 1
    message = str()
    for message_str in args:
        message += message_str

    fmessage = f"[OK] {message}"
    colored_message = f"{ansi.GREEN}{fmessage}"

    # write to logs.
    log_wrapped[log.id] = colored_message
    log_no_color[log.id] = fmessage


class __formatted:
    """
    Formats for the ID string
    """

    def __init__(self, id, error_id=0):
        self.error_log_id_format = f"[ error id: {error_id}::(log_id: {id}) ]:"
        self.log_id_format = f"[ message id: {id} ]:"


def print_log():
    for id, message in log_wrapped.items():
        print(f"{ansi.PURPLE}{__formatted(id).log_id_format}  {message}")
    print(f"{ansi.BLUE}== [ END OF MAIN THREAD ] ==\n")
    # print the errors
    for (error_id, id), error in log_errors.items():
        print(f"{ansi.PURPLE}{__formatted(id, error_id).error_log_id_format}:\n{
              ansi.RED}{ansi.UNDERLINE}{error}")


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
        for id, message in log_no_color.items():
            logfile.write(f"{__formatted(id).log_id_format}\n{message}\n")
        logfile.write("== [ END OF MAIN THREAD ] ==\n")

        # write the errors.
        for (error_id, id), error in log_errors.items():
            logfile.write(
                f"{__formatted(id, error_id).error_log_id_format}\n{error}\n")
    logfile.close()
    print(f"logfile written to {logfile}")


if __name__ == "__main__":
    write("hello", "world", "no")
    notify("[THIS IS A NOTIFICATION]", '\n\tdo something')
    error("this", "\nis an ", "error")
    read_log()
