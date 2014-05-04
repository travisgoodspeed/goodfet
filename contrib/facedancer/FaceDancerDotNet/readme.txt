This is a port of the FaceDancer Class as well as many of the supporting classes to VB.Net.
I've kept the structure for the most part as close as possible to the original python, although those might not necessarily be the best ways of doing things in .Net.

The Facedancer-Keyboard test definitely works as does the monitor test.
There is a USB Passhtrough device class that is in progress, and should work for simple things (I ran into problems with the unidirectional endpoints on the Max3421 when the device I was passing through had bidirectional ones).
It could obviously be much simpler, it doesn't REALLY need a special interface class, endpoints etc. It could just override the basic handle_events procedure and pass everything on to the real device without even looking at it,
caring what it's descriptor is, etc.

Adam Stasiak
palesius@gmail.com
9/3/2013
