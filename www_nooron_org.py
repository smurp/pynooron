#!/usr/local/Zope-2.5.1/bin/python

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: www_nooron_org.py,v 1.1 2003/04/02 13:43:50 smurp Exp $'


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

UID = 'nooron'
default_place = cwd+'/know' 
#default_place = cwd+'/pyokbc/tests'

from OkbcOperation import IPListSecurityEngine 
security_engine = IPListSecurityEngine(allow=['192.168.1.14',
                                              '24.52.220.140',
                                              '24.52.220.146',
                                              '208.38.8.158'],
                                       deny=1)

import __main__

__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = 'crusty',
                    server_ip = '216.194.67.142',
                    site_front = 'www_nooron_org_front.html',
                    server_port = 80,
                    log_to = sys.stdout,
                    initargs = {'default_place':default_place},
                    security_engine=security_engine,
                    cache_dir = '/tmp/nooron_cache')


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