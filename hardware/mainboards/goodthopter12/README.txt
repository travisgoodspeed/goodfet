GoodThopter12 CAN Adapter


IMPORTANT - "PLUG BUG FIX"

It turns out that OBD2 cables have a variety of pinouts for the DB9
connector.  The GoodThopter10 and GoodThopter11 used an expensive
cable from ICS, while this model prefers the Sparkfun cable that uses
different pins.  If your cable uses pins 3 and 5, then leave the board
as-is.  If your cable uses pins 7 and 3, then populate R6 and R8 with
zero-Ohm resistors and cut the traces to pins 3 and 5 as indicated on
the PCB.  For other pinotus, fly-wire the appropriate pins to the
labeled VIAs after cutting the necessary traces.

--

The GoodThopter is the sexy GoodFET CAN Adapter, whose purpose is to
route CAN connection from an automobile or ECU into a laptop
leveraging the maturing GoodFET firmware and project.  Care has been
taken to keep the design easy to solder and the code easy to modify.

If you like this project, the following will humbly accept beer
donations:

Andrew Righter, GoodThopter Project Lead
Travis Goodspeed, Circuit Preacher

CAN Hacking Inspired By:
-Late night drinking in the Midwest with Atlas and Cutaway.
-Late night drinking in Downtown Metropolitan Etna with Sergey Bratus
 singing ``Hop on the Magic School Bus!''
-Late night cramming in Philly to meet an absurd deadline that's
 demonstrably Andrew's fault, but without which you wouldn't have a
 neighborly GoodThopter.

If you have any questions/comments:

Andrew Righter <andrew@215LAB.com>

bugs/development:
http://goodfet.sf.net/
goodfet-devel@lists.sourceforge.net
