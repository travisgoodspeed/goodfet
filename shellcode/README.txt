Howdy y'all,

In addition to running code on the GoodFET itself (trunk/firmware) and
on the host (trunk/client), it is often necessary to run small
fragments of code on the target that is being debugged.  Rather than
allow each fragment to be written and edited as machine code, it is
better to write them in C in this directory, with the results being
dumped into trunk/client somehow.

Thank you kindly,
--Travis

