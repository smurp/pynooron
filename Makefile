
# $Revision: 1.7 $
# $Id: Makefile,v 1.7 2003/04/02 19:42:47 smurp Exp $

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

#tag:
#	cvs tag -R -D now nooron_0_2_8_1 .


test: 
	@echo $(PWD);
