
# $Revision: 1.2 $
# $Id: Makefile,v 1.2 2002/10/22 10:29:32 smurp Exp $

PWD     = $(shell /bin/pwd)
XTMTMP=$(shell mktemp /tmp/xtm.XXXXXX)
VERSION_NAME=$(shell cat version.txt)


make_help:
	echo "distro test"

distro:
	cd /tmp/ && \
	cvs export -r HEAD -d $(VERSION_NAME) nooron/pyokbc && \
	tar -cvzf $(VERSION_NAME).tgz $(VERSION_NAME) && \
	rm -fR $(VERSION_NAME)


test: 
	cd tests ; \
	./test_funcs.py
