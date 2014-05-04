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
   
   To experiment live, be sure to include the definitions from the
   appropriate section of config.mk.

*/


//Which holes are included?  Anything you leave out could probably be dremelled later.
cutusb=1;         // Almost always a good idea.

//Which side to render?
//rendertop=1
//renderbot=1

//Constants that will rarely change.
pcbheight=0.7;
wallthickness=2;
padding=1;


//Uncomment these for the GoodFET41.
//l=20;
//w=49;
//h=6;
//cutribbonslit=1;

//Uncomment these for the Facedancer10
//l=23.5;
//w=71;
//h=6;
//cutsecondusb=1;




//Render half the case at a time.
//More sophisticated locking would be appreciated.
difference(){
  goodfetcase(l+padding,
	      w+padding,
	      h+padding);
  
  if(rendertop==0){
    translate([-50,-50,0])
      cube(size=[100,100,100]);
  }
  if(renderbot==0){
    translate([-50,-50,-100])
      cube(size=[100,100,100]);
  }
}


//This is the case itself, cut from a cube.
module goodfetcase(l,w,h){
  difference(){
    //Exterior shell.
    cube(size=[l+wallthickness*2,
	       w+wallthickness*2,
	       h+wallthickness*2],
	 center=true);
    
    //Internal shell cut from it.
    color("red") translate([0,0,0]) 
      cube(size=[l,w,h],
	   center=true);
    
    //Further cut the USB plug.
    //TODO measure USB for accuracy.
    if(cutusb==1)
      #color("green") translate([0,-(w/2+wallthickness),0])
	cube(size=[l-6,6,2*h],
	     center=true);
    
    //Cut out the second USB plug for a Facedancer.
    //TODO measure second USB for accuracy.
    if(cutsecondusb==1)
      #color("green") translate([0,(w/2+wallthickness),0])
	cube(size=[l-6,6,2*h],
	     center=true);
    
    //Cut out the third USB plug for a Facedancer2x.
    if(cutthirdusb==1) //6.25/2
      #color("green") translate([6.25/2-wallthickness,(w/2-14.6/2+wallthickness/2),-h*1.4])
	cube(size=[14.5,14.7+wallthickness,2*h],
	     center=true);
    
    
    //Cut out a slit for the 14-pin ribbon.
    //Might be apropriate to increase PCB height.
    if(cutribbonslit==1)
      #color("green") translate([0,(w/2+wallthickness),0])
	cube(size=[l-2,8,2],
	     center=true);
    
    //Cut out the end to expose the 14-pin header.
    //Much cleaner to use the slit, as this will kill your pockets.
    //TODO Does the pin exposure work?
    if(cutpins==1){
      
      /*
	This cut is needed to let pins fit through the bottom.  Higher
	wall thickness might be a good idea, or the cut could be
	omitted if the plastic were softened by a hot-air gun and then
	the PCB pushed into it.
	
      */
      
      #color("green") translate([0,20,0])
	cube(size=[l-2,8,20],
	     center=true);
      
      
      //This cut provides for the top of the plug.
      #color("green") translate([0,(w/2-wallthickness),1])
	cube(size=[l+10,20,h+wallthickness],
	     center=true);
      
    }
    
  }
}
