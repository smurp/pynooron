
__version__='$Revision: 1.4 $'[11:-2]
__cvs_id__ ='$Id: NooronRoot.py,v 1.4 2002/08/02 18:47:18 smurp Exp $'

"""
NooronRoot is the root object of a nooron instance.

It is a singleton. Or rather a Borg:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531

"""
import os
import http_request_mixin
import TMObject_mixin

from TemplateManager import TemplateManager
import topicmap_handler
import code_handler
import PipeLineFactory
from medusa import http_server, default_handler, logger, filesys, status_handler

class NooronRoot:
    __shared_state = {}
    fsroot = None
    http_server = None
    pipeline_factory = None
    uri_root = '/'
    title = ''
    def __init__(self,publishing_root=None,
                 server_name=None,server_port=None,log_to=None,
                 use_auth = 0,
                 title = ''):
        self.__dict__ = self.__shared_state
        if not self.__dict__.has_key('prepped'):
            self.__dict__['prepped'] = 1

            if len(title): self.title = title
            
            self._template_root = TemplateManager(self,'templates')
            statusable_handlers = []
            
            if server_name and server_port and log_to:
                lg = logger.file_logger(log_to)
                hs = http_server.http_server(server_name,server_port,logger_object = lg)
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
                ch = code_handler.code_handler(fs,list_directories = 1,
                                               serve=['/code','/templates','/topicmap'],
                                               skip=['code/CVS','templates/CVS'])
                hs.install_handler(ch)
                statusable_handlers.append(ch)                

            tmh = topicmap_handler.topicmap_handler('know')            
            statusable_handlers.append(tmh)            
            
            if use_auth:
                ah = auth_handler({'guest':'password'},tmh)
                statusable_handlers.append(ah)
                hs.install_handler(ah)
            else:
                hs.install_handler(tmh)

            sh = status_handler.status_extension(statusable_handlers)
            hs.install_handler(sh)
            
            hs.install_handler(self)
            

    def make_fname(self,frag):
        if type(frag) == type([]):
            frag = os.path.join(frag[0],frag[1])
        return os.path.join(self.fsroot,frag)

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


if __name__ == "__main__":
    nooron1 = NooronRoot()
    nooron2 = NooronRoot()
    nooron1.system_basepath = '/home/smurp/src/nooron'
    print nooron1.system_basepath
    print nooron2.system_basepath
    print nooron1,nooron2
    #print nooron3['arf']
