#!/usr/bin/python2.1 

__version__='$Revision: 1.27 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.27 2003/01/24 12:26:41 smurp Exp $'


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""

import os
import sys
import asyncore

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

import __main__

__main__.__builtins__.nooron_root = \
         NooronRoot(publishing_root = cwd,
                    #server_name = 'crusty',
                    server_ip = '192.168.1.11',
                    site_front = 'www_nooron_org_front.html',
                    server_port = 9001,
                    log_to = sys.stdout,
                    initargs = {'default_place':default_place})


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

#print "final pid =",os.getpid()

asyncore.loop()
