# Logging Library
This folder contains all the code for our verbosity and logging system.

It depends on the arguments.py in the root modules folder, and the ANSI
libary in order to produce colored logging messages.

## Verbosity.
If the user specifies that they want the script to run in verbose mode,
the function `verbose_messaging()` is called in each message.

It's overall function is to print to `STDERR` with the message that the logging
system receives. 

In earlier versions of python-sat, the log would be printed at very end of the
program. However, as of v1.2.5+, messages will print in relative 'real-time',
with about a 100ms of delay in-between.
