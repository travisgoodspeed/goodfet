-include config.mk


all:
	board=facedancer11 make stl
	board=facedancer21 make stl
	board=goodfet42 make stl
	board=goodthopter11 make stl
stl:
	openscad -s $(board)_bot.stl -D renderbot=1 -D rendertop=0 $(config) goodfetlib.scad
	openscad -s $(board)_top.stl -D renderbot=0 -D rendertop=1 $(config) goodfetlib.scad
clean:
	rm -f *.stl *~
