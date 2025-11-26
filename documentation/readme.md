# Documentation and Reflection

Python-SAT was developed as the final project for my introduction to programming
course at Loyola University. Of which, there was a ton of things that I had used
from my experience as a developer outside of the course to satisfy both the requirements,
and the needs for this project to function.

This project uses a concurrency-based model to interact with servers hosting TCP based services,
such as websites and other TCP based protocols. I had not had the opportunity to add a check for 
UDP based connections, but they will eventually be supported at a later date.

This document serves not only to explain my thought process, but also as a reflection piece
to explain more about the project.

# Table of contents.

**Introduction**
- [Why was this written?](<#Why-was-this-written>)
  - [Three Step Process](<#The-3-step-process>)


**[Design and Pseudocode](<#Design-and-Pseudocode>)**
- [How does python-SAT work?](<#How-it-works>)
- [Why use TOML?](<#Why-TOML>)
- [Networking](<#Connectivity>)
  - [Handling Threads](<#Handling-Threads>)
- [Tables](<#Tables>)
  - [Issues with tables](<#Tables-Issues>)
- [Logging](<#Logging>)
- [Coloring Output](<#Coloring-Output>)

**[Developing For Other Platforms](<#Developing-for-other-platforms>)**
- [Setuptools](<#Setuptools>)
- [Install Script](<#The-Install-Script>)

**[Conclusive Thoughts](<#Conclusive-Thoughts>)**
- [My message to students](<#For-students>)
- [Contact Info](<#Contact>)

# Introduction

## Why was this Written
Prior to my tenure at Loyola, I have had a load of experience in my homelab setting up servers,
securing them, and configuring them. One issue I had constantly kept running into was the failure of
certain services, of which I had to diagnose the issues through numerous command line
inputs. I would have to ensure that the server was able to be reached with ICMP echoes,
and use tools such as `nmap` to see what ports were communicating. Previously, this had resulted
in a collection of bash scripts to do the very same process that this project does, and it became
quite cumbersome to scroll through lines of text to check the health of my servers.

Knowing how tedious that process can be, I have always had a desire to script the process to produce
simpler outputs so that I can just check for the essentials:

### The 3-step process

1. Is the server pingable?
2. Are the important ports communicating?
3. Is this specific port opened or closed?

Quite literally in that order.

I had designed this project specifically for server administrators who have to practically repeat this 
very same process over and over again-- and doing that for a load of servers can become quite the task.

Python-SAT was designed to do perform this process in bulk using a configurable file. Python was almost
the perfect language for this as it has many features that allow this process to be completed within the
standard library.

# Design and Pseudocode

## How it works

As mentioned before, python-SAT works on a concurrency-based model. What does that mean? Why is that important?
When interfacing with devices over a network, it is important to realize that those devices can fail
connections. Because of this, instead of performing connections based on iteration, it makes more sense to 
thread the process in such a way that one thread works per machine.

We can examine how this project fundamentally works through the flow chart below: 

![concurrency_model](https://github.com/merci-libre/python-sat/blob/main/blobs/concurrency.svg)

Essentially, the whole project relies on the features iterating over a list of threads, and
on each `rejoin()` we reprint our table displaying the connections to the user.


## Why TOML

.toml  produces a readable file that is super-easy to modify in comparison to something like .json
(JavaScript Object Notation) or .xml (eXtensive Markup Language). Not only is it super-easy to
modify and understand the syntax, but python (as of version 3.11) has direct support in its [standard
library](#https://docs.python.org/3/library/tomllib.html) for parsing toml files into hashtables (dictionaries).

As I want this project to be as accessible as possible to both developers and server administrators--
.toml allows me to reach both parties as it doesn't take a rocket scientist to read or parse through
what exactly is happening. 

(I also .toml because Rust familiarized me with it lol.)

## Connectivity

See the source code:

- [connectivity.py](https://github.com/merci-libre/python-sat/blob/main/sat/modules/connectivity/__init__.py)

Network connections was probably the most interesting feature for me to implement in this project.
Mostly because I have never have had to go as far as making raw socket connections in any of my other
software, but python-SAT handles network connections quite eloquently.

The connectivity library is where the majority of our threads will be reading and writing data throughout
the runtime of the program. From the parsed .toml file, we get our list of IP's and sockets that we want
to make connections to. 

Initially, I wanted to make my own ICMP library for this project, but got really frustrated that I had to
be escalate privileges to make those specific packets for my project to send-- since I was manually crafting
the ICMP packet rather than letting the kernel.

To solve this, I opted for using icmplib, which had pretty much all the functions required 
to make the ICMP packet, AND send them without prompting for a root login. The way it did that 
was by allowing the kernel to write the headers of the packets, which for the life of me, I could have never
figured out how to get working in the time span that I had for this project.

As for the majority of the other networking principles, I had written SAT in such a way that it would 
utilize the TCP 4-way handshake to determine whether the port was active or inactive, which worked perfectly
when I was testing it against TCP ports on my headless webserver machine where I have to make SSH connections
to manage it.

However, what I had not accounted initially was websockets. I had thought since that HTTP(S) was a TCP based
connection-- I would be able to detect those ports as open when scanning them. What I had not realized until
this project was that the HTTP protocol works entirely different and only uses TCP as a surrogate for
connections.

This means that a raw socket connection over standard TCP would not register the socket as open even though
there was a web server being hosted on the other end. To solve this, I had to use the HTTP protocol over those
specified ports in-order to register them as `open`. We do this by making a `GET` request to the server in
conjunction with a standard TCP packet and if both of those fail, we can safely assume that the server is not
working properly. In later versions, I may opt for testing `POST` requests, but there are other better tools
out there for that specific type of testing.

To better visualize this, please see the annotated screenshot of a .pcap made in my presentation here:

![pcap](https://github.com/merci-libre/python-sat/blob/main/blobs/pcap.png)

### Handling Threads

As I had mentioned in the first section of this document, each thread is assigned to completing connections
through this library in particular. We do so with the `test()` function which completes that 
[3 step process](<#The-3-step-process>) that I had outlined in the first section. It first checks if the server
is pingable, if not-- we close the thread. If it does respond to the ICMP echoes, and the user has ports that 
they want to scan, then the program then scans those ports.

Meanwhile, each thread is simultaneously writing the results to a hashmap where the data on each server is stored.
In concurrency-based operations, this can be a little-scary, as writing data to a shared object among threads can
lead to a race-condition, where 2 threads are trying to write to the same place in memory at the same time.

This issue occurs if the user-defines multiple servers with the same IP, as that IP is the only unique
identifier that the program uses to writing to that hashmap. I have yet to implement a solution, but I have thought
of doing:

- Using the server title as the key if they share the same IP (multiple definitions of the same object causes an 
exception with toml as there can't be duplicate keys) 
- Dropping identical IP's before the threads are loaded to prevent the race conditions.

Of which, the latter is the easiest to implement.

## Tables

See the source code:

- [tables.py](https://github.com/merci-libre/python-sat/blob/main/sat/modules/tables/__init__.py)

All features dealing with the tables will be ascribed to the 
[tables.py](https://github.com/merci-libre/python-sat/blob/main/sat/modules/tables/__init__.py)
library. The way this works is by iterating over a dictionary, and writing the results from
[connectivity.py](https://github.com/merci-libre/python-sat/blob/main/sat/modules/connectivity/__init__.py)
to the table. 

However, this introduces an interesting problem: Everytime we finish a task through a `rejoin()` we have
to reprint the table with updated information. So we need to include an argument to the function that
notifies it when it should clear the tables with the private method: `__clear_table()`.

This way, the user isn't spammed with `n` tables for every server that they want to check.

### Tables Issues

There is some standing issues with the tables:

1. They don't play nice on Windows [(see here)](<#Developing-for-other-platforms>)
2. If a user decides to fill the box longer than xxx.xxx.xxx.xxx characters, the table breaks uniform.
3. Ports can print to the next line if scanning for more than the width of the table, meaning I have to reformat
the table if the user wants to scan for an absurd amount of ports.

## Logging

See the source code:

- [log.py](https://github.com/merci-libre/python-sat/blob/main/sat/modules/log/__init__.py)

This one was by far the feature I was most proud of implementing. The logging library
was one of the most useful things that I could have implemented in this entire project.
I had used it in another project as well after I had wrote it for this one, of which I
can't share the repository since it's private, but it was really useful when I was rewriting
a one of the scripts we used for monitoring a PLC machine for Cyberforce 2025.

The logging system was inspired by other logging libraries used in OpenBSD's OpenSSH Daemon, and
[Log4j's logging framework for java](https://github.com/apache/logging-log4j2).

Using a logging library a multi-threaded program such as SAT was extremely helpful when debugging issues 
within the threads as they silently print out the information for me, I had left it as a feature for the project
not only for other developers to use when they make their own additions or features to the source code.

Even for future features such as daemonizing the program, these logs will tell a user when exactly a thread failed
to make a connection, and print it out with the timestamps of when they occured.

This also allows me to note where I should be looking when making optimizations, as the timestamps give me
an idea of how long the process takes to complete, as well as all the other important information that I might
need such as packet loss, and HTTP responses.

There are 5 type of log messages:

- Start Messages. `log.start()`
These are added when the logging system starts a new process, and when the main thread starts.

- Errors Messages. `log.error()`
These get printed when an error occurs that is recoverable, unrecoverable errors cause python-SAT
to crash with a special message, and a traceback.

- Notification Messages. `log.notify()`
These notify when important functions are running, or when there is a response from a socket.

- Information Messages. `log.info()`
These give extra tidbits of information on the connections, and the data within the program
at runtime.

- OK messages. `log.write()`
These get printed to notify that the program succeeded with an operation, or when a positive outcome is achieved.

Of which, all error notifications get printed at the very bottom of the screen, before printing the table.
This allows the user to see when exactly those errors occur, and what went wrong during the program's runtime
in one place.

## Coloring output

As you can see when running the project, we print in color! This is because we use ANSI escape codes to print-out
colors. I added all the colors you could possibly use in a standard terminal-- but not all get used. 

This is because I may add more configuration later to customize the output of the tool!

If you're interested on what ANSI escape codes are check out this 
[wikipedia article!](https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit)

# Developing for other platforms
During my time researching and developing this project, I had realized that other users might want to 
use this script. Of course my system is rather 'unique' as it retains less market share than other 
Operating Systems-- and my system in particular handles things very differently.

So I had to spend some time figuring out how I could make this project as portable as
possible, and so I came up with this plan for development:

1. I develop for *nix (Linux) machines first.
2. I develop for MacOS second (they're *almost* Unix-like)
3. ~I develop for Windows third.~

Unix machines were the easiest, since I daily drive one, meaning that I'm testing natively.

For Windows and other Linux Distributions it was rather easy since I could just pop-up a virtual 
machine using QEMU/KVM and then develop the tool in the environment.

For MacOS-- I had to borrow someone's MacBook to test if the install script and project worked,
and everytime it didn't I had to rewrite the project for it to work universally. 

I eventually got the project working on Debian Linux (and its derivatives), Arch Linux, and MacOS.

Noticed how I haven't mentioned **Windows**? Let me explain:

With Windows, when things **should work**-- they didn't.

Because python-SAT uses specific unicode characters when printing-- 
it has made development for Windows an absolute pain. If this project had taught me
anything about the development process-- it's that NT based systems are the absolutely 
worst platform to develop for with python. For other languages I can compile using Windows
instructions-- but since Python is interpreted, I have to play nice with the Windows API. 

Windows would not be an issue had I used any other standard characters for printing the tables.
I would have considered more time fixing this issue-- had the **unicode characters not work on 
every single other operating system** that I had tested Python-SAT on.

This frustrated me so much to the point that I decided that I was not going to support a build
on Windows, and that if they do wish to use this tool-- they need to install and use the 
Windows Subsystem for Linux-- which I did test on (and it worked...)

## Setuptools
Because I had to build for Mac, I realized that I would need to create a wheel file for them
to use `pip` to install this package. Since I already had `build` and `setuptools`, I decided
that this would be the build system that I would use for my project. Plus `setuptools` used
toml files for it's configuration, which I already had experience with from developing in Rust.

## The Install Script
Of course, what good is a program if a user can't use it?

The install script is another thing that I am really proud of. It checks the user's operating system
and installs the program based on that. For Linux users, it automatically picks up on which package
manager it should use, and installs the dependencies for system-packages automatically, and installs
the program to the user's computer to the `/usr/local/bin` and `/usr/lib/python{VERSION}/site-packages/`
directory. It also detects whether the user is using `doas` or `sudo` for their substitute user command.

For Linux users, it automatically loads the `install.sh` command with all of the arguments required for install.
Uninstalling uses `subprocess`, as the uninstall process is less command intensive.

For MacOS users, it just installs with pip, because MacOS doesn't need to deal with externally managed packages
with the VENV like Linux does.

# Conclusive Thoughts
I had really enjoyed creating this project. For me-- developing things comes from a place of love, and joy.
I had always loved building things, and to each time I make something-- I try to learn something new along the
way; This final project had me learn things about concurrency, build-systems, and most importantly-- building for
other operating systems without the comfort of something like `cargo`-- which has built-in compiling tools for other
operating systems and architectures.

Python is a very intricate language-- I had usually avoided it from the massive amount of overhead it had in memory usage,
but this class has taught me that it can be such a versatile scripting language. This project has shown me how
complex this language can be, and I'm excited to learn more about software design and principles as I attend Loyola.


## For Students

If you are a student from class who wanted to check my project, I want to thank you for spending the extra time going and
reading about my project. I hope that it had taught you something that you can use in future classes should you continue
learning more about programming and software design. I have never worked in a professional environment, but I have spent many
years learning how to program and learning about computers generally. 

With that said, I don't want you to think that you need to be at this level if you aren't. My project was built not to intimidate
or to 'flex' but because I wanted to build something that would be useful for myself, and others. This was more than a final project
to me-- it became my passion project.


## Contact

If you're interested in asking me more about my project-- or pick my brain on computers, I advise you to email me:

- Professional email: jvillanueva7@luc.edu 
- or my dev email: westwardfishdme@gmail.com

We can exchange contact info there, and I would be more than happy to explain this project, answer any questions about my experience,
or just talk about computers!

-- Thanks + :3

Finch/Westwardfishdme/Jonathan Villanueva
