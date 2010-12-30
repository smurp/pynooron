#!/usr/local/Zope-2.5.1/bin/python

import os
import sys
import asyncore

sys.path.append('code')
from NooronRoot import NooronRoot

import string

cwd = os.getcwd()

UID = 'nooron'
kr_root = '/home/nooron/knowledge/'
places = [kr_root+'apps_of/nooron',
          kr_root+'apps_of/smurp',          
          kr_root+'apps_of/givingspace',
          kr_root+'apps_of/idcommons',
          kr_root+'apps_of/demo',
          kr_root+'apps_of/kaliya',
          kr_root+'nooron_apps',
          kr_root+'nooron_foundations',
          cwd+'/know']
#default_place = cwd+'/pyokbc/tests'

import login_handler

from users import dict_of_users
use_auth = login_handler.dictionary_authenticator(dict_of_users)

from AuthenticatedUserAuthorizer import AuthenticatedUserAuthorizer
security_engine = AuthenticatedUserAuthorizer()

import __main__
__main__.__builtins__.wedge_string = '__'
__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = 'crusty',
	            server_ip = '72.47.237.232',
                    site_front = 'www_nooron_org_front.html',
                    server_port = 8000,
                    log_to = sys.stdout,
                    use_auth = use_auth,
                    initargs = {'default_place':string.join(places,':')},
                    knowledge_under = 'know',
                    security_engine=security_engine,
                    cache_dir = '/home/nooron/tmp/nooron_cache')


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
