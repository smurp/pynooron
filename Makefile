
# $Revision: 1.6 $
# $Id: Makefile,v 1.6 2002/12/17 09:05:49 smurp Exp $

PWD     = $(shell /bin/pwd)
VERSION_NAME=$(shell cat version.txt)


make_help:
	echo "distribution all"

distribution:
	cd /tmp/ && \
	cvs export -r HEAD nooron && \
	mv nooron $(VERSION_NAME) && \
	tar -cvzf $(VERSION_NAME).tgz $(VERSION_NAME) && \
	rm -fR $(VERSION_NAME)

test: 
	@echo $(PWD);
