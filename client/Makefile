#This is a py2exe Makefile for the Windows port, which is only
#maintained when Travis gets stuck doing MSP430 manufacturing.

prefix=/usr/local

link:
	rm -f $(prefix)/bin/goodfet.* $(prefix)/bin/goodfet $(prefix)/bin/facedancer*
	rm -rf *~
	mkdir -p $(prefix)/bin
	ln -s `pwd`/goodfet `pwd`/goodfet.* `pwd`/facedancer* $(prefix)/bin/
install:
	echo "Try 'make link' instead."

py2exepub:
#publish the windows build.
	rsync --exclude .svn -ave ssh --progress --chmod=a+rx tmp/goodfet.zip travisutk,goodfet@web.sourceforge.net:htdocs/dist/gfwin.zip
py2exeinstall: py2exe
	rm -rf "c:\goodfet\bin"
	md "c:\goodfet\bin"
	copy tmp\\goodfet\\* c:\\goodfet\\bin\\
	rem Be sure to add C:\goodfet\bin to %Path%.
py2exe:
#Run this from Win32 with Python, py2exe, py-serial, and GNU utils.
#MSP430 Client
	sed s/PYTHONCONSOLE/goodfet.msp430/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gf430.exe
#Monitor
	sed s/PYTHONCONSOLE/goodfet.monitor/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfmon.exe
#JTAG
	sed s/PYTHONCONSOLE/goodfet.jtag/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfjtag.exe

#BSL
	sed s/PYTHONCONSOLE/goodfet.bsl/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfbsl.exe
#AVR
	sed s/PYTHONCONSOLE/goodfet.avr/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfavr.exe
#PIC
	sed s/PYTHONCONSOLE/goodfet.pic/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfpic.exe
#Chipcon SPI
	sed s/PYTHONCONSOLE/goodfet.ccspi/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfccspi.exe
#Chipcon
	sed s/PYTHONCONSOLE/goodfet.cc/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfcc.exe
#SPI Flash
	sed s/PYTHONCONSOLE/goodfet.spiflash/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfspi.exe
#Nordic RF
	sed s/PYTHONCONSOLE/goodfet.nrf/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfnrf.exe
#RF
	sed s/PYTHONCONSOLE/goodfet.rf/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfrf.exe
#25C SPI EEPROM
	sed s/PYTHONCONSOLE/goodfet.spi25c/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfspi25.exe
#Silicon Labs C2
	sed s/PYTHONCONSOLE/goodfet.slc2/ <p2e.txt >setup.py
	python setup.py py2exe
	mv dist/goodfet.exe dist/gfslc2.exe

#Goodfet.  This must be last.
	sed s/PYTHONCONSOLE/goodfet/ <p2e.txt >setup.py
	python setup.py py2exe
#	mv dist/goodfet.exe dist/goodfet.exe
#Now package it all.
	rm -rf tmp
#mkdir -p tmp/goodfet
	md tmp\goodfet
	mv dist/* tmp/goodfet/
	cd tmp && zip -r goodfet.zip goodfet

