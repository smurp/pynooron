
# $Revision: 1.2 $
# $Id: Makefile,v 1.2 2002/07/11 17:17:39 smurp Exp $

PWD     = $(shell /bin/pwd)
XTMTMP=$(shell mktemp /tmp/xtm.XXXXXX)


XTMS = nooron.xtm

.SUFFIXES: .atm .xtm

.atm.xtm:
	astma2xtm.pl < $< > $@

all: xtm mysql

mysql: empty_mysql psi 
	~/bin/gwq -i -g "type=MySQL,name=nooron,user=smurp,pass=trivialpw" file://$(PWD)/nooron.xtm;

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
