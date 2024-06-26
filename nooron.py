#!/usr/bin/env python

__version__='$Revision: 1.36 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.36 2003/04/30 15:21:34 smurp Exp $'


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

import string

cwd = os.getcwd()

UID = 'smurp'
default_place = cwd+'/know' 
#default_place = cwd+'/pyokbc/tests'

import login_handler
from users import dict_of_users
use_auth = login_handler.dictionary_authenticator(dict_of_users)


import __main__

__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = 'crusty',
                    server_ip = '192.168.1.14',
                    site_front = 'www_nooron_org_front.html',
                    server_port = 80,
                    log_to = sys.stdout,
                    initargs = {'default_place':default_place},
                    knowledge_under = None,
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
