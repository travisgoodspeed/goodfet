Chipcon 8051 Random Test
Neighborware by Travis Goodspeed

This short little application connects to a Chipcon CC2430, then dumps
random numbers from the PRNG.  Some ZigBee stacks make the mistake of
using this for key data, allowing an attacker to try all 65,534 possible
keys in short order.

As two bytes are sampled per byte returned, you will see two sets of
2**32-1 bytes repeated.  Once a device begins on one set, it will not
switch to the other unless reseeded.  It is also possible that both
bytes might be sampled, yielding a different arrangement of the same
bytes.

