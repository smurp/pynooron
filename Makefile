
# $Revision: 1.5 $
# $Id: Makefile,v 1.5 2002/08/23 03:39:14 smurp Exp $

PWD     = $(shell /bin/pwd)
XTMTMP=$(shell mktemp /tmp/xtm.XXXXXX)
VERSION_NAME=$(shell cat version.txt)

XTMS = nooron.xtm

.SUFFIXES: .atm .xtm

.atm.xtm:
	astma2xtm.pl < $< > $@

make_help:
	echo "distribution all"

distribution:
	cd /tmp/ && \
	cvs export -r HEAD nooron && \
	mv nooron $(VERSION_NAME) && \
	tar -cvzf $(VERSION_NAME).tgz $(VERSION_NAME) && \
	rm -fR $(VERSION_NAME)


all: xtm mysql

mysql: empty_mysql psi 
	~/bin/gwq -i -g "type=MySQL,name=nooron,user=smurp,pass=trivialpw" file://$(PWD)/topicmap/smurp_web_log.xtm;

xtm:
	astma2xtm.pl < nooron.atm > nooron.xtm

pretty: #xtm
	prettifyxtm.pl < nooron.xtm > ${XTMTMP} ;
	cat ${XTMTMP} > nooron.xtm;
	rm $(XTMTMP);

empty_mysql:
	mysql nooron < /usr/local/src/gwtk/sql/mysql.sql 

psi:
	~/bin/gwq -i -g "type=MySQL,name=nooron,user=smurp,pass=trivialpw" http://www.topicmaps.org/xtm/1.0/psi1.xtm;

test: 
	@echo $(PWD);

test2: $(XTMS)
	echo BOO!
