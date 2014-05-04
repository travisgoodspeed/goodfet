all:
	make get
	make goodfet.kml
	make put
clean:
	rm -f goodfet.kml
get:
	rsync -ave ssh n9:/sdcard/goodfetlog.txt ./
goodfet.kml: goodfetlog.txt
	cat goodfetlog.txt | ./goodfetlog2kml.py >goodfet.kml
put: goodfet.kml
	rsync -avze ssh --progress goodfet.kml goodfetlog.txt cumberland.travisgoodspeed.com:htdocs/
open: goodfet.kml
	open goodfet.kml
