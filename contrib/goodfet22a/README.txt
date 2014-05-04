This design is a somewhat modified version of the GoodFET22 design.

Okay, I completely redrew it because I wanted to use the
more-commonly-available QFP-80 MSP430F2618 part, and I wanted to be
able to use the extra GPIOs for another project (a NOR flasher).  I
also made some changes to the glitching section of the circuit -- I
switched to using a different MUX chip (also easier to find), and I
added a couple of opamps configured as voltage followers to buffer the
voltage coming out of the DAC outputs.  I also wanted to use Altium
Designer instead of Eagle, so here we are.

As of 4/2010, I've successfully built several of these and used them
as NOR flashers; I have not yet actually tried soldering on either the
MUX or the op-amp; YMMV.

I tried to stay true to the GoodFET22 design so that the software
would be mostly compatible, but I ended up moving around some of the
pin assignments so that I could have the most contiguous pin groups to
use as an address and data bus and to make the layout easier.
Unfortunately, this means that the GoodFET code will require some
slight changes to support operation of the target port; specifically,
I moved the following signals:

Signal	   	 GoodFET22     GoodFET22a

GSEL		 P5.7	       P1.4
target_TMS	 P5.0	       P3.0
target_TDI	 P5.1	       P3.1
target_TDO	 P5.2	       P3.2
target_TCK	 P5.3	       P3.3
target_RST	 P2.6	       P1.3
TEST		 P4.0	       P1.2

Your reward for making these slight changes will be 64 usable GPIOs,
all broken out to pin headers.  Enjoy!

bushing@gmail.com, April 2010
