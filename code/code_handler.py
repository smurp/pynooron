
__version__='$Revision: 1.7 $'[11:-2]
__cvs_id__ ='$Id: code_handler.py,v 1.7 2002/12/12 14:00:19 smurp Exp $'


"""Serve up the /code/ directory as described at 
   http://www.noosphere.org/discuss/zwiki/Nooron"""

DEBUG = 0

import string
from medusa.default_handler import *
from medusa import default_handler
from medusa import producers

import NooronRoot
from DirectoryFacade import DirectoryFacade

import transformers
from debug_tools import timed

class path_handler(default_handler.default_handler):
    def __init__ (self, filesystem, list_directories = 0,serve=[],skip=[],
                  just_serve = []):
        self.filesystem = filesystem
        # count total hits
        self.hit_counter = counter()
        # count file deliveries
        self.file_counter = counter()
        # count cache hits
        self.cache_counter = counter()
        self.list_directories = list_directories 
        self.serve = serve
        self.just_serve = just_serve # ie, do not set content-type to text/plain
        self.skip = skip

    @timed
    def match(self,request):
        path = request.split_uri()[0][1:]
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



class code_handler(path_handler):
    def set_content_type (self, path, request):
        for js in self.just_serve:
            if path.startswith(js):
                default_handler.default_handler.set_content_type(self,path,request)
                return
        request['Content-Type'] = 'text/plain'

