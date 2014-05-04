/* Parametric GoodFET Case
   by Travis Goodspeed
   for the GoodFET41 and related models.
   
   This is an OpenSCAD model intended for generating 3D cases for the
   GoodFET family of boards.  Specific revisions have been tested on
   the Makerbot Replicator 2 in PLA, but any neighbor who is involved
   in 3D printing knows that you'll have to experiment a little or a
   lot to get anything of use.
   
   I expect a half dozen forks of this to come about, but I ask that
   you post them either on Github or in the /contrib/ region of the
   GoodFET repository.  Other neighbors will find your examples handy,
   however ugly the code might be.
   
   Edit this file to experiment, but the bulk of the code is in
   goodfetlib.scad.  Release models are defined in config.mk.

*/


//Are we rendering the top or the bottom?
//Change these to render the individual pieces.
rendertop=0;
renderbot=1;

//Uncomment these for the GoodFET41.
//l=20;
//w=49;
//h=6;
//cutribbonslit=1;

//Uncomment these for the Facedancer10
l=23.5;
w=71;
h=6;
cutsecondusb=1;
cutthirdusb=1;

//Include the library, but don't run its code.
include<goodfetlib.scad>
