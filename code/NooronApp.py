
__version__='$Revision: 1.6 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.6 2002/09/27 19:01:23 smurp Exp $'

import GW
from GWApp import GWApp

import NooronRoot

class NooronApp(GWApp):

    __allow_access_to_unprotected_subobjects__ = 1
    
    src_uris = []
    app_skeleton = []

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
        npt_name = ""
        args = {}
        this_is_app_front = 0
        if not topic_obj:
            print "there is no topic_obj, determining ..."
            bname_contains = self.getAllWhereBaseNameContains
            bname_is = self.getAllWhereBaseNameIs
            app_instance = bname_contains('app instance') or \
                           bname_is('app instance') 
            if app_instance:
                app_instances = app_instance[0].getInstances()
                if app_instances:
                    this_is_app_front = 1                    
                    topic_obj = app_instances[0]
        if not topic_obj:
            topic_obj = self
        if this_is_app_front:
            npt_name = self.npt_for_app_front(request,topic_obj)
        if not npt_name:
            npt_name = self.get_template_for_topic(request,topic_obj)
        if __debug__: print "npt_name = ",npt_name
        if npt_name:
            request.effective_query_extend({'with_template':
                                            npt_name})
        NooronRoot.NooronRoot().publish(request,topic_obj)

    def npt_for_app_front(self,request,topic_obj):
        print "topic_obj = "+str(topic_obj)
        occs = topic_obj.getOccurrences()#typ='npt for app front')
        # relies on typ-sensitivity in getOccurrences
        occs = None
        if occs:
            print "we got occs! " + str(len(occs))
            print str(occs[0][2].getSCR().getUris()[0])
            print str(occs[1][2].getSCR().getUris()[0])
            return str(occs[0][2].getSCR().getUris()[0])

    def get_template_for_topic(self,request,topic_obj):
        query = request.split_query()
        return query.get('with_template') or \
               self.npt_for_self(request,topic_obj) or \
               self.npt_for_instances(request,topic_obj)

    def npt_for_instances(self,request,topic_obj):
        clsses = topic_obj.getClasses()
        for clss in clsses:
            some = clss.getOccurrences(typ='npt_for_instances')
            if some:
                return str(some[0][2].getSCR().getUris()[0])
        print "no npt_for_instances found"
        
    def npt_for_self(self,request,topic_obj):
        #some = topic_obj.getOccurrences()
        #some = topic_obj.getOccurrences(typ='npt_for_self')
        some = topic_obj.getOccurrences(typ='nooron_app_architecture.xtm#npt_for_self')
        if some:
            #self.print_occurrenceResources(topic_obj)
            for i in some:
                print "--> " + str(i[2].getSCR().getData())
            return str(some[0][2].getSCR().getUris()[0])
        print "failing to find npt_for_self"

