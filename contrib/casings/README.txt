Howdy y'all,

This directory contains OpenSCAD scripts for parametric GoodFET
casings.  Compile them with the included Makefile, then print the .STL
files on your 3D printer.  Watch out for curling, lifting, and damned
near every other hassle of these infernal contraptions, and the result
just might fit.

Top and bottom case halves are generated separately, and they hold
together quite well with super glue.  For some designs, the top and
bottom are identical.  Feel free to fork these for your own projects
or to post tested builds to Shapeways and Thingiverse.

Files are as follows:

goodfet.scad    -- For use in OpenSCAD when making a new design.
goodfetlib.scad -- Library for generating most GoodFET cases.
Makefile        -- So you're not stuck with a GUI.
config.mk       -- Contains board dimensions and features for release.

Cheers,
--Travis Goodspeed



