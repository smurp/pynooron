__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: okbc_handler.py,v 1.2 2002/10/18 07:21:02 smurp Exp $'


from pyokbc import *

import NooronApp

DEBUG = 0

from medusa import counter
import medusa
from medusa.default_handler import unquote

class okbc_handler:
    def __init__(self,from_root,connection=None):
        self.hits = counter.counter()
        self.exceptions = counter.counter()
        self.from_root = from_root
        self.connection = connection

    def status(self):
        prod = medusa.producers.simple_producer
        return prod("openable kbs:" + str(openable_kbs(self.connection)))

    def match(self,request):
        [path, params, query, fragment] = request.split_uri()
        retval = path.find(self.from_root)
        if retval < 0:
            retval = 0
        if DEBUG: print "okbc_handler %s %s\n" % (path,str(retval))
        return retval

    def handle_request(self,request):
        [path, params, query, fragment] = request.split_uri()
        # path extensions query
        while path and path[0] == '/':
            path = path[1:]

        if '%' in path or '+' in path:
            path = string.replace(path,'+',' ')
            path = unquote (path)
            print path

        frame_in_kb_p = 0
        frame = None
        kb = None

        path_list = path.split('/')
        if len(path_list) < 3 and path[-1] != '/':
            loc = '/%s/' % (
                path
                )
            request['Location'] = loc
            print "FIXME: is it legal to forward to root-relative url?"
            request.error (301) # moved permanently
            return

        if path_list[-1] == '':
            del path_list[-1]

        if len(path_list) == 1:
            kb = meta_kb()

        if len(path_list) > 1:
            kb_name = path_list[1]
            kb = open_kb(kb_name)
            if not kb:
                request.error(401) # not found
                return

        app = NooronApp.NooronApp(kb)
        
        if len(path_list) > 2:
            frame_name = path_list[2]
            frame_name = frame_name.replace('+',' ')
            app.publish(request,frame_name)
        else:
            app.publish(request)





    def junk_pile(self):
        if frame_in_kb_p:
            app.publish(request,frame)
        else:
            app.publish(request,kb)
        
        #print NooronRoot.the_root,NooronRoot.booger
        if frame_in_kb_p:
            #NooronRoot.the_root.publish(request,frame)
            nooron_root.publish(request,frame)
        else:
            #NooronRoot.the_root.publish(request,kb)
            nooron_root.publish(request,frame)            
            #NOORON_ROOT.publish(request,frame)            
            #NooronRoot.NooronRoot().publish(request,kb)            
