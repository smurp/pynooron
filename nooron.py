#!/usr/bin/python2.1 

__version__='$Revision: 1.23 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.23 2002/12/06 20:46:17 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore

# adjust for your Zope installation
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python/Products')

sys.path.append('code')
from NooronRoot import NooronRoot

cwd = os.getcwd()

default_place = cwd+'/know' 
#default_place = cwd+'/pyokbc/tests'

import __main__

__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    server_name = '192.168.1.11',
                    server_port = 8081,
                    log_to = sys.stdout,
                    initargs = {'default_place':default_place})

asyncore.loop()
