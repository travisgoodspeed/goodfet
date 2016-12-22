#
# Raspdancer
#
# Implementation of the Facedacner API that supports direct access to the MAX324x
# chip via a RasPi's SoC SPI bus. Emulates talking to a Facedancer, but ignores
# the details of the GreatFET protocol.
#

from Facedancer import *

import spi
import RPi.GPIO as GPIO

# List all of the verbs supported by the MaxUSB app we're emulating.
READ  = 0x00
WRITE = 0x01
PEEK  = 0x02
POKE  = 0x03
SETUP = 0x10

# The application number for the MAXUSB App.
MAXUSB_APP = 0x40

class Raspdancer(Facedancer):
    """
        Extended version of the Facedancer class that accepts a direct
        SPI connection to the MAX324x chip, as used by the Raspdancer.
    """

    def __init__(self, verbose=0):
        """
            Initializes our connection to the MAXUSB device.
        """
        self.verbose = verbose
        self.buffered_result = b''
        self.last_verb = -1

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        self.reset()

    def halt(self):
        """
            Halts communication with the MAXUSB.
        """
        print("HALT: Not yet implemented!")

    def reset(self):
        """
            Resets the connected MAXUSB chip.
        """
        GPIO.setup(15, GPIO.OUT)
        GPIO.output(15,GPIO.LOW)
        GPIO.output(15,GPIO.HIGH)

    def read(self, n):
        print("READ: Not yet implemented!")

    def write(self, b):
        print("WRITE: Not yet implemented!")

    def readcmd(self):
        """
            Reads the result of a previous GreatFET command.
        """
        result = FacedancerCommand(MAXUSB_APP, self.last_verb, self.buffered_result)

        if self.verbose > 1:
            print("Facedancer Rx command:", result)

        return result

    def writecmd(self, c):
        """
            Executes a given GreatFET command, emualting an issue of the 
            command to the Facedancer's GoodFET.
        """

        handlers = {
            READ: self.issue_read,
            WRITE: self.issue_write,
            SETUP: self.issue_setup,
            PEEK: self.issue_peek,
            POKE: self.issue_poke
        }

        if self.verbose:
            print("Facedancer Tx command:", c)

        # If we have a function that handles the given command, execute it.
        if c.verb in handlers:
            handler = handlers[c.verb]

            self.buffered_result = handler(c.data)
            self.last_verb = c.verb

        # Otherwise, report that we don't support the given verb.
        else:
            print("VERB {}: currently unsupported!".format(c.verb))


    def issue_setup(self, data):
        """
            Sets up the Raspdancer to communicate with the MAX324x.
        """
        # pin15=GPIO22 is linked to MAX3420 -RST
        GPIO.setup(15, GPIO.OUT)
        GPIO.output(15,GPIO.LOW)
        GPIO.output(15,GPIO.HIGH)

        spi.openSPI(speed=26000000)

        return b''


    def issue_write(self, data):
        """
            Emulate the facedancer's write command, which blasts data
            directly over to the SPI bus.
        """
        if isinstance(data,str):
            data = [ord(x) for x in data]

        data = tuple(data)
        data = spi.transfer(data)

        return bytearray(data)

    def issue_read(self, data):
        """
            Emulate the facedancer's read command, which blasts data
            directly over to the SPI bus.
        """
        return self.issue_write(data)


    def issue_peek(self, data):
        """
            Emulate the facedancer's peek command.
        """

        # Currently, this command does nothing on the MSP430.
        return b''


    def issue_poke(self, data):
        """
            Emulate the facedancer's poke command.
        """

        # Currently, this command does nothing on the MSP430.
        return b''

