gflpc1343 - an experimental GoodFET based on the LPC1343

contributed by Michael Ossmann <mike@ossmann.com>

designed with KiCad: http://www.kicad-pcb.org

This is an experimental hardware design.  Firmware for this board does not
(yet?) exist.

It is made to fit the 40x40 mm Sick of Beige case:

http://dangerousprototypes.com/docs/Sick_of_Beige_standard_PCB_sizes_v1.0

I added a second 14 pin header for expansion.  It has I2C (with pull-ups),
ADC, timer, and GPIO pins.  Both headers have enough room so that shrouded
connectors may be installed to protect the pins.

There is an SWD debug header and an ISP programming header.  Both are SMD pads
on the right hand side of the board (one on top and one on the bottom).  They
can be used with spring pins, or SMD headers can be soldered on.  They're at
the edge, so through hole pins can be soldered on edgewise if preferred.  I
don't expect that either header would be used by most people, though, as the
USB bootloader should be sufficient.

I tried to make it no more difficult to hand-assemble than the past designs
apart from having more components.  The smallest parts are 0603s.  Since the
LPC1343 includes a USB bootloader in ROM, hand assembly may be done with no
additional programming hardware (similar to the MSP430/FTDI designs).

My idea for the expansion header is that daughterboards could plug in to both
of the 14 pin headers for mechanical stability (similar to Arduino shields).
There could be an nRF board that supports the NHB code, a MAX3420 board that
supports the Facedancer code, etc.
