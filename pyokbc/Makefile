
# $Revision: 1.1 $
# $Id: Makefile,v 1.1 2002/10/22 10:28:38 smurp Exp $

PWD     = $(shell /bin/pwd)
XTMTMP=$(shell mktemp /tmp/xtm.XXXXXX)
VERSION_NAME=$(shell cat version.txt)


make_help:
	echo "distribution test"

distribution:
	cd /tmp/ && \
	cvs export -r HEAD -d $(VERSION_NAME) nooron/pyokbc && \
	tar -cvzf $(VERSION_NAME).tgz $(VERSION_NAME) && \
	rm -fR $(VERSION_NAME)


test: 
	cd tests ; \
	./test_funcs.py
