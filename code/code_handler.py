
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: code_handler.py,v 1.2 2002/07/29 22:37:50 smurp Exp $'


"""Serve up the /code/ directory as described at 
   http://www.noosphere.org/discuss/zwiki/Nooron"""

DEBUG = 0

import string
from medusa.default_handler import *
from medusa import default_handler
from medusa import producers

from NooronRoot import NooronRoot
from DirectoryFacade import DirectoryFacade

from transformers import typed_file_producer

class code_handler(default_handler.default_handler):
    def __init__ (self, filesystem, list_directories = 0,serve=[],skip=[]):
        self.filesystem = filesystem
        # count total hits
        self.hit_counter = counter()
        # count file deliveries
        self.file_counter = counter()
        # count cache hits
        self.cache_counter = counter()
        self.list_directories = list_directories 
        self.serve = serve
        self.skip = skip

    def match(self,request):
        path = request.split_uri()[0]
        indx = self.allowable(path) and \
               self.filesystem.isdir(path) or self.filesystem.isfile(path)
        if DEBUG: print path, self.filesystem.wd,indx
        return indx != 0

    def allowable(self,path):
        allowed = 1
        # FIXME partial path match error 
        if self.serve:
            allowed = 0
            for direct in self.serve:
                if string.find(path,direct) == 0:
                    #print "allowing ",direct
                    allowed = 1
                    break
        if self.skip:
            for direct in self.skip:
                if string.find(path,direct) == 0:
                    #print "disallowing ",direct                    
                    allowed = 0
                    break
        #print path," allowable = ",allowed
        return allowed


    def handle_request(self,request):
        if request.command not in self.valid_commands:
            request.error(400) # bad request
            return

        self.hit_counter.increment()

        
        path, params, query, fragment = request.split_uri()

        if '%' in path:
            path = unquote (path)

        # strip off all leading slashes
        while path and path[0] == '/':
            path = path[1:]

        if self.filesystem.isdir(path):
            if path and path[-1] != '/':
                request['Location'] = 'http://%s:8081/%s/' % (
                    request.channel.server.server_name,
                    path
                    )
                print "FIXME: forwarding not including port automatically"
                request.error (301) # moved permanently
                return
            obj = DirectoryFacade(path)
        elif self.filesystem.isfile(path):
            obj = typed_file_producer(open(path,'ro'))
        else:
            request.error(401)
            return

        pl = NooronRoot().pipeline_factory.build_pipeline(request,obj)
        pl.publish()
        
    

