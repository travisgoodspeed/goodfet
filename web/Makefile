NANOC:=nanoc

compile: 
	$(NANOC) compile
upload: compile
	rsync --exclude .svn -ave ssh output/* travisutk,goodfet@web.sourceforge.net:htdocs/
releases: upload
	rsync --exclude .svn -ave ssh ../../branches/*.zip travisutk,goodfet@web.sourceforge.net:htdocs/releases/
clean:
	rm -rf output tmp
auto:
	$(NANOC) autocompile
