
__version__='$Revision: 1.5 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.5 2002/08/23 03:39:15 smurp Exp $'

import GW
from GWApp import GWApp

import NooronRoot

class NooronApp(GWApp):

    __allow_access_to_unprotected_subobjects__ = 1
    
    src_uris = []

    def set_src_uris(self,src_uris):
        self.src_uris = src_uris
    
    def getTopicWithAnchor(self,anchor):
        for uri in self.src_uris:
            a_name = "%s#%s" % (uri,anchor)
            one = self.getTopicWithID(a_name)
            if one:
                return one
        else:
            return None

# see http://www.noosphere.org/discuss/zwiki/VariousTemplateUseCases
    def publish(self,request,topic_obj):        
        args = {}
        if not topic_obj:
            bname_contains = self.getAllWhereBaseNameContains
            bname_is = self.getAllWhereBaseNameIs
            app_instance = bname_contains('app instance') or \
                           bname_is('app instance') 
            if app_instance:
                app_instances = app_instance[0].getInstances()
                if app_instances:
                    topic_obj = app_instances[0]
        if not topic_obj:
            topic_obj = self
        npt_name = self.get_template_for_topic(request,topic_obj)
        if __debug__: print "npt_name = ",npt_name
        if npt_name:
            request.effective_query_extend({'with_template':
                                            npt_name})
        NooronRoot.NooronRoot().publish(request,topic_obj)

    def get_template_for_topic(self,request,topic_obj):
        query = request.split_query()
        return query.get('with_template') or \
               self.npt_for_me(request,topic_obj) or \
               self.npt_for_instances(request,topic_obj)

    def npt_for_instances(self,request,topic_obj):
        clsses = topic_obj.getClasses()
        for clss in clsses:
            some = clss.getOccurrences(typ='npt_for_instances')
            if some:
                return str(some[0][2].getSCR().getUris()[0])
        
    def npt_for_me(self,request,topic_obj):
        some = topic_obj.getOccurrences(typ='npt_for_me')
        if some:
            return str(some[0][2].getSCR().getUris()[0])

