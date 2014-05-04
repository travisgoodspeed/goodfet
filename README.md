GoodFET
=======

The GoodFET is a nifty little tool for quickly exposing embedded
system buses to userland Python code.

Drivers
-------

For Mac, install XCode, MacPorts, and the FTDI Virtual COM Driver.

For Windows, install Python 2.7 as 32-bit, FTDI VCP Drivers,
and add Python your %PATH% in order to run the scripts in \client.

In Linux, the FTDI drivers are included by default.  Be sure that the
user has permissions for /dev/ttyUSB0, which will likely require
adding that user to the dialout group.

Packages
--------

You will need python-serial, wget, gcc-msp430, and curl.  These might
have different names, and the MSP430 compiler might be separated from
its libc implementation.


