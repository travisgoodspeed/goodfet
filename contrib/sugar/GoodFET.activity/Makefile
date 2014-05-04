
all: dist 

manifest: sources
	rm -rf MANIFEST dist
	find . -type f | grep -v MANIFEST | sed 's,^./,,g'  >MANIFEST
dist: manifest
	./setup.py dist_xo
dev: manifest
	./setup.py dev
clean:
	rm -rf MANFIFEST dist GoodFET.py GoodFETCCSPI.py
sources:
	cp ../../../trunk/client/GoodFET.py ./
	cp ../../../trunk/client/GoodFETCCSPI.py ./