__version__='$Revision: 1.9 $'[11:-2]
__cvs_id__ ='$Id: okbc_handler.py,v 1.9 2002/11/27 07:53:10 smurp Exp $'


from pyokbc import *

import NooronApp

DEBUG = 0

from medusa import counter
import medusa
from medusa.default_handler import unquote

wedge = '__'
    
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
        #if DEBUG: print "okbc_handler %s %s\n" % (path,str(retval))
        return retval

    def handle_request(self,request):
        [path, params, query, fragment] = request.split_uri()
        # path extensions query
        #print "======\n\n"
        while path and path[0] == '/':
            path = path[1:]

        if '%' in path or '+' in path:
            path = string.replace(path,'+',' ')
            path = unquote (path)
            #print path


        frame = None
        kb = None
        npt_name = None

        path_list = path.split('/')
        if len(path_list) < 3 and path[-1] != '/':
            loc = '/%s/' % (
                path
                )
            request['Location'] = loc
            #print "FIXME: is it legal to forward to root-relative url?"
            request.error (301) # moved permanently
            return

        if path_list[-1] == '':
            del path_list[-1]

        if len(path_list) == 1:
            kb = meta_kb()
            app = NooronApp.MetaKB(kb)
            app.publish(request)
            return

        for elem in [self.from_root]:
            print "checking",elem
            if str(elem) == str(path_list[0]):
                path_list.pop(0)
        print "path_list",path_list

        latest_kb = meta_kb()
        for elem in path_list:
            print "seeking",elem
            frag = string.split(elem,wedge)
            if len(frag) == 2:
                elem = frag[0]
                npt_name = frag[1]
            (frame,found_frame_p) =  get_frame_in_kb(elem,kb=latest_kb)
            if frame != None:
                if kb_p(frame):
                    print elem,"is a kb"
                    latest_kb = frame
                else:
                    print elem,"is a frame"
            else:
                print elem,"was not found in",lastest_kb

        print "kb",latest_kb,"frame",elem
        app = NooronApp.GenericFrame(latest_kb)
        app.publish(request,elem,npt_name)

