#!/usr/local/Zope-2.5.1/bin/python

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: localhost.py,v 1.1 2003/04/30 15:21:34 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore

# adjust for your Zope installation
sys.path.append('/usr/local/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/Zope-2.5.1/lib/python/Products')
sys.path.append('/usr/local/Zope-2.5.1/ZServer')

sys.path.append('code')
from NooronRoot import NooronRoot

import string

cwd = os.getcwd()

UID = os.getuid()
kr_root = '/home/smurp/knowledge/'
places = [kr_root+'apps_of/nooron',
          kr_root+'apps_of/smurp',          
          kr_root+'apps_of/givingspace',
          kr_root+'apps_of/demo',
          kr_root+'apps_of/kaliya',
          kr_root+'nooron_apps',
          kr_root+'nooron_foundations',
          cwd+'/know']
#default_place = cwd+'/pyokbc/tests'

#from OkbcOperation import IPListSecurityEngine 
#security_engine = IPListSecurityEngine(allow=['192.168.1.14',
#                                              '24.52.220.*',
#                                              '208.38.8.158'],
#                                       deny=1)

import login_handler

use_auth = login_handler.friendly_favors_authenticator(\
    group_key_map={'GS':'4009e3fa8d42a0f8fac49932f6b5fcb8'},
    fqdn = "www.smurp.com")

use_auth = login_handler.bogus_favors_authenticator()

from AuthenticatedUserAuthorizer import AuthenticatedUserAuthorizer
security_engine = AuthenticatedUserAuthorizer()

import __main__
__main__.__builtins__.wedge_string = '__'
__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = 'crusty',
                    server_ip = 'localhost',
                    site_front = 'www_nooron_org_front.html',
                    use_auth=use_auth,
                    server_port = 8001,
                    log_to = sys.stdout,
                    initargs = {'default_place':string.join(places,':')},
                    knowledge_under = 'know',
                    security_engine=security_engine,
                    cache_dir = '/tmp/www_nooron_org_cache')


try:
    import pwd
    try:
        #try:    UID = string.atoi(UID)
        #except: pass
        gid = None
        if type(UID) == type(""):
            uid = pwd.getpwnam(UID)[2]
            gid = pwd.getpwnam(UID)[3]
        elif type(UID) == type(1):
            uid = pwd.getpwuid(UID)[2]
            gid = pwd.getpwuid(UID)[3]
        else:
            raise KeyError 
        try:
            if gid is not None:
                try:
                    os.setgid(gid)
                except OSError:
                    pass
            os.setuid(uid)
        except OSError:
            pass
    except KeyError:
        print "can not find UID %s" % UID
except:
    pass

use_monitor = 0
if use_monitor:
    from medusa.monitor import *
    monitor_password = None
    monitor_encrypt = 0
    monitor_port = 8023
    if monitor_password is not None:
        s = secure_monitor_server (monitor_password, '', monitor_port)
        if monitor_encrypt:
            s.channel_class = secure_encrypted_monitor_channel
            import sapphire
            s.cipher = sapphire
    else:
        s = monitor_server ('', monitor_port)
        
#print "final pid =",os.getpid()

asyncore.loop(use_poll=1)
