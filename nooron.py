#!/usr/bin/python2.1 

__version__='$Revision: 1.15 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.15 2002/08/14 20:47:42 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore

import GW
#print dir(GW)
#GW.setTrace('*')

# adjust for your Zope installation
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python/Products')

sys.path.append('code')
from NooronRoot import NooronRoot

cwd = os.getcwd()

maps = {'weblog':'file://%s/topicmap/weblog.xtm' % cwd,
        'howto_config_an_app':'file://%s/topicmap/howto_config_an_app.xtm' % cwd,
        'smurp_web_log':'file://%s/topicmap/smurp_web_log.xtm' % cwd,
        'nooron_site_config':'file://%s/topicmap/nooron_site_config.xtm' % cwd,
        'blog':'file://%s/topicmap/blog.xtm' % cwd,
        #'denial':'file://%s/topicmap/DenialOfServiceAttacks.xtm' % cwd,
        #'contacts':"http://topicmaps.bond.edu.au/examples/contacts.xtm",
        #'contacts':'file:///download/knowledge/contacts.xtm',
        'jill':'file:///download/knowledge/jill.xtm',
        #'random':'http://www.random.com/sumpin.xtm',
        #'whatever',"type=MySQL,name=dbname,user=yourname,pass=yourpw",
        'smurp':'file://%s/topicmap/smurp_as_agent.xtm' % cwd}

maps = 'topicmap/nooron_site_config.xtm'

NooronRoot(publishing_root = cwd,
           #server_name = '192.168.1.11',
           server_name = '',
           server_port = 8081,
           log_to = sys.stdout,
           initial_maps = maps)
    
asyncore.loop()



