#Generates distribution files for all targets.
#Testing is performed separately.

gfpath?=goodfet
fwpath=$(gfpath)/firmware
hwpath=$(gfpath)/hardware
clientpath=$(gfpath)/client
#testpath=$(gfpath)/tests


all:
	rm -rf dist
	mkdir dist
	echo "Options +Indexes" >dist/.htaccess
	rm -rf $(gfpath)
	git clone https://github.com/travisgoodspeed/goodfet
	#cd $(testpath) && make nodiff 
	cd $(fwpath) && board=goodfet11 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodfet11.hex >/dev/null
	cd $(fwpath) && board=goodfet41 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodfet41.hex >/dev/null
	cd $(fwpath) && board=goodfet42 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodfet42.hex >/dev/null
	cd $(fwpath) && board=goodfet31 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodfet31.hex >/dev/null
	cd $(fwpath) && board=telosb make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/telosb.hex >/dev/null
	cd $(fwpath) && board=z1 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/z1.hex >/dev/null
	cd $(fwpath) && board=facedancer10 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/facedancer10.hex >/dev/null
	cd $(fwpath) && board=facedancer11 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/facedancer11.hex >/dev/null
	cd $(fwpath) && board=facedancer20 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/facedancer20.hex >/dev/null
	cd $(fwpath) && board=facedancer21 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/facedancer21.hex >/dev/null
	cd $(fwpath) && board=goodthopter10 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodthopter10.hex >/dev/null
	cd $(fwpath) && board=goodthopter11 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodthopter11.hex >/dev/null
	cd $(fwpath) && board=goodthopter12 make clean all >/dev/null 2>>/dev/null
	cp $(fwpath)/goodfet.hex dist/goodthopter12.hex >/dev/null
	cp $(clientpath)/*.py $(clientpath)/goodfet.* dist
	cp distreadme.txt dist/README.txt
	cd dist && zip `date +goodfet-%Y-%m-%d.zip` *
clean:
	rm -rf *.hex *~ $(gfpath)
upload: all
	rsync --exclude .svn -ave ssh --delete dist travisutk,goodfet@web.sourceforge.net:htdocs/
