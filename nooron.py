#!/usr/bin/python2.1

__version__='$Revision: 1.10 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.10 2002/08/02 23:53:40 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore

sys.path.append('code')
from NooronRoot import NooronRoot

cwd = os.getcwd()

maps = {'weblog':'file://%s/weblog.xtm' % cwd,
        #'jill':'file:///download/knowledge/jill.xtm',
        #'random':'http://www.random.com/sumpin.xtm',
        #'whatever',"type=MySQL,name=dbname,user=yourname,pass=yourpw",
        'smurp':'file://%s/smurp_as_agent.xtm' % cwd}

NooronRoot(publishing_root = cwd,
           #server_name = '192.168.1.11',
           server_name = '',
           server_port = 8081,
           log_to = sys.stdout,
           initial_maps = maps)

asyncore.loop()

