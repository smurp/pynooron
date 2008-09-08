#!/usr/bin/env python

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: prom.py,v 1.1 2008/09/08 02:15:29 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore
from medusa.monitor import *

# adjust for your Zope installation
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python/Products')

sys.path.append('code')
from NooronRoot import NooronRoot
import login_handler

import string

cwd = os.getcwd()

UID = 'smurp'
default_place = cwd+'/know' 

print "cwd = ",cwd
kr_root = '/home/smurp/knowledge/'
places = [kr_root+'apps_of/nooron',
          kr_root+'apps_of/smurp',          
          #kr_root+'apps_of/givingspace',
          kr_root+'apps_of/demo',
          kr_root+'apps_of/kaliya',
          kr_root+'nooron_apps',
#          kr_root+'nooron_foundations',
          cwd+'/know']

#default_place = cwd+'/pyokbc/tests'

##from OkbcOperation import IPListAuthorizer
##security_engine = IPListAuthorizer(allow=['192.168.1.14',
##                                          '24.52.220.100',
##                                          '24.52.220.*',
##                                          '208.38.8.158'],
##                                   deny=1)

use_auth = login_handler.dictionary_authenticator({'guest1':'pw1',
                                                   'guest2':'pw2'})

#use_auth = login_handler.friendly_favors_authenticator(\
#    group_key_map={'GS':'4009e3fa8d42a0f8fac49932f6b5fcb8'},
#    fqdn = "www.smurp.com")

#use_auth = login_handler.bogus_favors_authenticator()

from AuthenticatedUserAuthorizer import AuthenticatedUserAuthorizer
security_engine = AuthenticatedUserAuthorizer()

template_path = ['/home/smurp/templates','templates']
import __main__
__main__.__builtins__.wedge_string = '__'
__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = 'crusty',
                    server_ip = '192.168.1.14',
                    site_front = 'www_nooron_org_front.html',
                    server_port = 9001,
                    log_to = sys.stdout,
                    use_auth = use_auth,
                    initargs = {'default_place':string.join(places,':')},
                    template_path = template_path,
                    knowledge_under = 'know',
#                    just_serve = [{'fs_path':'/tmp/TS','http_path'='TS'}],
                    just_serve = [cwd+'/htdocs'],
                    security_engine=security_engine,
                    cache_dir = '/tmp/nooron_cache'
                    #cache_dir = None
                    )


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
