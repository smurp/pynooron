#!/usr/bin/python2.1

__version__='$Revision: 1.5 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.5 2002/07/23 18:33:37 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

DEBUG = 1

PUBLISHING_ROOT='/home/smurp/src/nooron'

import time
import string,os,re
import sys

# Medusa support
import asyncore
from medusa import http_server
from medusa import default_handler
from medusa import logger
from medusa import script_handler
from medusa import filesys
from medusa import status_handler
from medusa import producers
from medusa import counter

# nooron-specific modules
sys.path.append('code')
import inspect_module
import transformers
import PipeLineFactory
import topicmap_handler
import code_handler

global NooronRoot
from NooronRoot import NooronRoot



lg = logger.file_logger (sys.stdout)

# code_dh <== NR/code/*
fs = filesys.os_filesystem (PUBLISHING_ROOT + "/code",wd="/code")
code_dh = code_handler.code_handler (fs)
#code_dh = default_handler.default_handler (fs)

pipelineFactory = PipeLineFactory.PipeLineFactory()

# the topicmap_handler (to be spruced up with extension smarts)
tmh = topicmap_handler.topicmap_handler('map',pipelineFactory)
tmh.import_topicmap('jill','file:///download/knowledge/jill.xtm')

tmh.import_topicmap('weblog','file:///home/smurp/src/nooron/weblog.xtm')
#tmh.import_topicmap('catalog','file:///home/smurp/src/nooron/catalog.xtm')
#tmh.import_topicmap('opera','file:///download/knowledge/opera.xtm')
#tmh.import_topicmap('nooron','file:///home/smurp/src/nooron/nooron.xtm')


hs = http_server.http_server ('', 8081, logger_object = lg)
sh = status_handler.status_extension([hs,tmh,pipelineFactory])
hs.install_handler(sh)

nooron_root = NooronRoot()
nooron_root.fsroot = PUBLISHING_ROOT
nooron_root.http_server = hs

hs.install_handler(tmh)
#hs.install_handler(code_dh)

asyncore.loop()

