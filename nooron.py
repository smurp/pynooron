#!/usr/bin/python2.1

__version__='$Revision: 1.8 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.8 2002/08/02 18:47:18 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import time
import string,os,re
import sys
import asyncore

sys.path.append('code')
from NooronRoot import NooronRoot


NooronRoot(publishing_root = '/home/smurp/src/nooron',
           server_name = '192.168.1.11',
           server_port = 8081,
           log_to = sys.stdout)

asyncore.loop()

