#!/usr/bin/python2.1 

__version__='$Revision: 1.17 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.17 2002/10/21 08:34:04 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore

#import GW
#print dir(GW)
#GW.setTrace('*')

# adjust for your Zope installation
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python/Products')

sys.path.append('code')
from NooronRoot import NooronRoot

cwd = os.getcwd()

default_place = cwd+'/know' # FIXME should use os.pathjoin (sp?)

import __main__


#if not hasattr( __main__.__builtins__, 'nooron_root' ):
__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = '192.168.1.11',
                    server_name = '',
                    server_port = 8081,
                    log_to = sys.stdout,
                    initargs = {'default_place':default_place})

asyncore.loop()



