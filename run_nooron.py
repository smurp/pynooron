#!/usr/bin/env python
__version__= open('version.txt').read()
__doc__ = """
  The program run_nooron.py offers command line options to start
  a nooron instance on a port, at an IP, publishing knowledge and 
  using media to suit the user.
"""

def path_to_list(path):
    """ 
    >>> p = "a:b:c"
    >>> path_to_list(p)
    ['a', 'b', 'c']

    >>> list_to_path(path_to_list(p)) == p
    True
    
    """
    return path.split(":")
def list_to_path(lst):
    return ":".join(lst)

import sys
import asyncore
import string
import os
cwd       = os.getcwd()
home_dir  = os.path.expanduser("~")
UID       = 'nooron'
kr_root   = '%(home_dir)s/knowledge/' % locals()
cache_dir = '%(home_dir)s/tmp/nooron_cache' % locals()
fqdn_and_port = "nooron.org" # or "nooron.org:8000"
default_port = '8000'
default_ip_address = '127.0.0.1'
default_media_path = list_to_path(["media","docs"])
default_site_front = "dogfood_front.html"
default_site_front = "www_nooron_org_front.html"
default_site_front = "simple_skin.html"
know_list = [kr_root+'apps_of/nooron',
             kr_root+'apps_of/smurp',          
             #kr_root+'apps_of/givingspace',
             #kr_root+'apps_of/idcommons',
             kr_root+'apps_of/demo',
             #kr_root+'apps_of/kaliya',
             kr_root+'apps_of/pod',
             kr_root+'nooron_apps',
             kr_root+'nooron_foundations',
#             cwd+'/pyokbc/tests',
             cwd+'/know']


def start_nooron(options,args):
    sys.path.append('code')
    sys.path.append('contrib')
    from NooronRoot import NooronRoot

    if options.cache_dir:
        cache_dir = options.cache_dir

    try:
        os.makedirs(cache_dir)
    except:
        pass

    import login_handler


    if options.htpasswd:
        if os.path.exists(options.htpasswd):
            use_auth = login_handler.htpasswd_authenticator(options.htpasswd)
        else:
            raise ValueError('htpasswd file %s does not exist, try:\n%s' % (
                    options.htpasswd,
                    "  contrib/htpasswd.py -c %s USER1 PW1" % options.htpasswd))

    from AuthenticatedUserAuthorizer import AuthenticatedUserAuthorizer
    security_engine = AuthenticatedUserAuthorizer()


    import __main__
    __main__.__builtins__.nooron_root = \
             NooronRoot(publishing_root = cwd,
                        server_name = options.fqdn_and_port,
                        server_ip = options.ip_address,
                        site_front = options.site_front,
                        just_serve = path_to_list(options.media_path),
                        server_port = options.port,
                        log_to = sys.stdout,
                        use_auth = use_auth,
                        #initargs = {'default_place':string.join(places,':')},
                        initargs = {'default_place':options.knowledge_path},
                        knowledge_under = 'know',
                        security_engine=security_engine,
                        cache_dir = cache_dir)


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

    from medusa.monitor import monitor_server,secure_monitor_server
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


if __name__ == "__main__":        
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--man",
                      action = 'store_true',
                      help = "show the manual for this program")
    parser.add_option("--port",
                      type="int",
                      default = default_port,
                      help = "the port for the server, default: %s" % default_port)
    parser.add_option("--ip_address",
                      type="str",
                      default = default_ip_address,
                      help = "dotted quad ip address to serve, default: %s" % default_ip_address)
    parser.add_option("--cache_dir",
                      type="str",
                      default = cache_dir,
                      help = "the directory to use as cache, default: %s" % cache_dir)
    parser.add_option("--fqdn_and_port",
                      type="str",
                      default = fqdn_and_port,
                      help = "the canonical url for the server, default: %(fqdn_and_port)s")
    parser.add_option("--htpasswd",
                      type="str",
                      default = ".htpasswd",
                      help = "path to htpasswd file to use for authentication, default: %(default_htpassword)s")
    parser.add_option("--knowledge_path",
                      type="str",
                      default = list_to_path(know_list),
                      help = "colon-separated path to knowledge, default: %s" % list_to_path(know_list))
    parser.add_option("--media_path",
                      type="str",
                      default = default_media_path,
                      help = "colon-separated path for static files, default: %s" % default_media_path)
    parser.add_option("--site_front",
                      type="str",
                      default = default_site_front,
                      help = "file to serve when / is hit, default: %s" % default_site_front)
    parser.add_option("--unittest",
                      action = 'store_true',
                      help = "perform unit tests")
    parser.add_option("-v","--version",
                      action = 'store_true',
                      help = "show version")
    parser.add_option("-V","--verbose",
                      action = 'store_true',
                      help = "be verbose in all things, go with god")
    
    if False:
        parser.add_option("--ini_file",
                          type="str",
                          help = "path to file containing ")
        parser.add_option("--dump_as_ini_file",
                          action = 'store_true',
                          help = "emit the current configuration in format for --ini_file ")
    

    parser.version = __version__
    parser.usage =  """
    e.g.
       %prog 
          start Nooron on localhost and port 8000

       %prog --ip_address 72.47.237.232 --port 8000
          start Nooron at a given ip and port (e.g. karaba)

    """ 
    (options,args) = parser.parse_args()
    if False:
        if options.dump_as_ini_file:
            print dir(options)
            #print repr(options),repr(args)
            os.exit()

    show_usage = True
    if options.unittest:
        show_usage = False
        import doctest
        doctest.testmod(verbose=options.verbose)
        sys.exit()
    if options.version:
        show_usage = False
        if options.verbose:
            print __cvs_id__
        else:
            print parser.version
    if options.man:
        show_usage = True
        import pydoc
        import sys
        #print __import__(__name__)
        pydoc.help(__import__(__name__))
    else:
        start_nooron(options,args)
    if show_usage:
        parser.print_help()
