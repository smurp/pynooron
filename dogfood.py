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

#from OkbcOperation import IPListSecurityEngine 
#security_engine = IPListSecurityEngine(allow=['192.168.1.14',
#                                              '152.163.188.*', # linda
#                                              '24.52.220.*',   # tom
#                                              '208.38.8.158'],
#                                       deny=1)

import login_handler

#use_auth = login_handler.friendly_favors_authenticator(\
#        group_key_map={'GS':'4009e3fa8d42a0f8fac49932f6b5fcb8'},
#            fqdn = "www.nooron.org")
#use_auth = login_handler.bogus_favors_authenticator()
use_auth = login_handler.dictionary_authenticator({'smurp':'badtemppw'})
#use_auth = login_handler.kb_authenticator('DevelopmentUsers')



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
