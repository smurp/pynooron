
__version__='$Revision: 1.24 $'[11:-2]
__cvs_id__ ='$Id: NooronRoot.py,v 1.24 2002/12/18 18:33:00 smurp Exp $'

DEBUG = 0

"""
NooronRoot is the root object of a nooron instance.

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
#import PipeLineFactory

from pyokbc import *
import NooronApp
import os


def npts_for_self_and_instances(here):
    npt_for_self = get_slot_values(here,'npt_for_self',
                                   slot_type=Node._all)[0] or \
                                   ['frame_details.html',
                                    'frame.html',
                                    'kb_ancestry.dot'];

    if class_p(here):
        npt_for_instances = get_slot_values(here,'npt_for_instances',
                                            slot_type=Node._template)[0]
    else:
        npt_for_instances = []
    return npt_for_self + npt_for_instances

def sort_frames(these):
    str_sort=lambda a,b: cmp(str(a),str(b))
    these.sort(str_sort)
    return these



class NooronRoot:
    fsroot = None
    http_server = None
    pipeline_factory = None
    uri_root = '/'
    title = ''
    def __init__(self,publishing_root=None,
                 server_name=None,server_port=None,log_to=None,
                 use_auth = 0, initargs = {},
                 site_front='site_front.html',
                 title = ''):
        #self.__dict__ = self.__shared_state
        self._initargs = initargs
        self._site_front = site_front
        # set up
        #print "initargs =",initargs
        os.environ["LOCAL_CONNECTION_PLACE"] = initargs['default_place']
        self._connection = local_connection()
        #put_direct_parents(['nooron_app_architecture.pykb'],
        #                   kb=self._connection.meta_kb())
        prim_kb = find_kb('PRIMORDIAL_KB')

        put_slot_values(':KB','npt_for_instances',
                        ['kb.html'],
                        kb=prim_kb,
                        slot_type=Node._template)

        put_slot_values(':THING','npt_for_self',
                        ['frame_details.html','frame.html'],
                        kb=prim_kb,
                        slot_type=Node._template)



        register_procedure('npts_for_self_and_instances',
                           kb=prim_kb,
                           procedure=\
                           create_procedure(body=\
                                            npts_for_self_and_instances))

        register_procedure('sort_frames',
                           kb=prim_kb,
                           procedure=create_procedure(body=sort_frames))



        meta = meta_kb()
        meta_direct_parents = get_kb_direct_parents(kb=meta)
        meta_direct_parents.append(open_kb('nooron_app_architecture'))
        
        meta.put_direct_parents(meta_direct_parents)

        put_slot_values(meta,'npt_for_self',
                        ['openable_kbs.html'],
                        kb=meta)

        #print "get_kb_direct_parents()",get_kb_direct_parents(kb=meta)

        #print "local_connection =",local_connection()
        #print "current_kb =",current_kb()        
        #print "openable_kbs =",openable_kbs(connection=local_connection())
        
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
                #print dir(hs)
                statusable_handlers.append(hs)                
            else:
                raise "IncompleteNooronRootSetup", \
                      'arguments server_name, server_port and log_to required'

            #self.pipeline_factory = None #PipeLineFactory.PipeLineFactory()
            #statusable_handlers.append(self.pipeline_factory)
            
            if publishing_root:
                self.fsroot = publishing_root
                fs = filesys.os_filesystem(self.fsroot)
                ch = code_handler(fs,list_directories = 1,
                                  serve=['/code','/templates'],
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
        #if DEBUG: print "make_fname",frag
        if type(frag) == type([]):
            frag = os.path.join(frag[0],frag[1])
        pth = os.path.join(self.fsroot,frag)
        normpath = os.path.normpath(pth)
        #if DEBUG: print "normpath =",normpath
        if normpath.find(self.fsroot) != 0:
            raise "Illegal path requested",\
                  "%s not in %s" % (normpath,self.fsroot)
        return normpath

    def template_root(self):
        return self._template_root

    def match(self,request):
        path = request.split_uri()[0]
        return path == '' or path == '/'

##    def publish(self,request,object,npt_name='',extensions=[]):
##        pl = self.pipeline_factory.build_pipeline(request,
##                                                  object,
##                                                  npt_name,
##                                                  extensions)
##        pl.publish()

    def handle_request(self,request):
        meta = meta_kb()
        request.set_object_request('/')
        app = NooronApp.GenericFrame(meta)
        app.publish(request,None,self._site_front,extensions=[])

#    def objectValues(self):
#        return []

    def __str__(self):
        return "Nooron Site Root"
