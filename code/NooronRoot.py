
__version__='$Revision: 1.8 $'[11:-2]
__cvs_id__ ='$Id: NooronRoot.py,v 1.8 2002/10/18 07:21:02 smurp Exp $'

DEBUG = 1

"""
NooronRoot is the root object of a nooron instance.

It is a singleton. Or rather a Borg:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531

"""
import os
from medusa import http_server, default_handler, logger
from medusa import filesys, status_handler

import http_request_mixin
import http_channel_mixin
#import TMObject_mixin

from TemplateManager import TemplateManager
#import topicmap_handler
import okbc_handler
from code_handler import code_handler
import PipeLineFactory

from pyokbc import *
import os

booger ='boo gear'
class NooronRoot:
    fsroot = None
    http_server = None
    pipeline_factory = None
    uri_root = '/'
    title = ''
    def __init__(self,publishing_root=None,
                 server_name=None,server_port=None,log_to=None,
                 use_auth = 0, initargs = {},
                 title = ''):
        #self.__dict__ = self.__shared_state
        self._initargs = initargs

        # set up
        #print "initargs =",initargs
        os.environ["LOCAL_CONNECTION_PLACE"] = initargs['default_place']
        self._connection = local_connection()
        
        if not self.__dict__.has_key('prepped'):
            self.__dict__['prepped'] = 1

            if len(title): self.title = title

            self._template_root = TemplateManager(self,'templates')
            statusable_handlers = []
            
            if server_name != None and server_port and log_to:
                lg = logger.file_logger(log_to)
                hs = http_server.http_server(server_name,server_port,
                                             logger_object = lg)
                self.http_server = hs
                statusable_handlers.append(hs)                
            else:
                raise "IncompleteNooronRootSetup", \
                      'arguments server_name, server_port and log_to required'

            self.pipeline_factory = PipeLineFactory.PipeLineFactory()
            statusable_handlers.append(self.pipeline_factory)

            if publishing_root:
                self.fsroot = publishing_root
                fs = filesys.os_filesystem(self.fsroot)
                ch = code_handler(fs,list_directories = 1,
                                  serve=['/code','/templates','/topicmap'],
                                  skip=['code/CVS','templates/CVS'])
                hs.install_handler(ch)
                statusable_handlers.append(ch)                

            kbh = okbc_handler.okbc_handler('know',
                                            connection = self._connection)
            #tmh = topicmap_handler.topicmap_handler('know',
            #                                        initial = initial_maps)
            statusable_handlers.append(kbh)
            
            if use_auth:
                ah = auth_handler({'guest':'password'},kbh)
                statusable_handlers.append(ah)
                hs.install_handler(ah)
            else:
                hs.install_handler(kbh)

            sh = status_handler.status_extension(statusable_handlers)
            hs.install_handler(sh)
            
            hs.install_handler(self)
            

    def make_fname(self,frag):
        if DEBUG: print "make_fname",frag
        if type(frag) == type([]):
            frag = os.path.join(frag[0],frag[1])
        pth = os.path.join(self.fsroot,frag)
        normpath = os.path.normpath(pth)
        if DEBUG: print "normpath =",normpath
        if normpath.find(self.fsroot) != 0:
            raise "Illegal path requested",\
                  "%s not in %s" % (normpath,self.fsroot)
        return normpath

    def template_root(self):
        return self._template_root

    def match(self,request):
        path = request.split_uri()[0]
        return path == '' or path == '/'

    def publish(self,request,object):
        pl = self.pipeline_factory.build_pipeline(request,object=object)
        pl.publish()

    def handle_request(self,request):
        self.publish(request,self)

    def objectValues(self):
        return []

