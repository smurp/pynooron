
__version__='$Revision: 1.8 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.8 2002/10/18 07:21:02 smurp Exp $'

#import GW
#from GWApp import GWApp

from pyokbc import *
import NooronRoot

class NooronApp:

    __allow_access_to_unprotected_subobjects__ = 1
    
    src_uris = []
    app_skeleton = []

    def __init__(app,kb):
        app._kb = kb

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
    def publish(app,request,frame_name=None):
        (frame,frame_found_p) = frame_name \
                                and app._kb.get_frame_in_kb(frame_name) \
                                or (None,None)
        npt_name = ""
        this_is_app_front = 0
        if not frame_found_p:
            npt_name = "kb_as_html"
            frame = app._kb
        if this_is_app_front:
            npt_name = self.npt_for_app_front(request,topic_obj)
        if not npt_name:
            npt_name = self.get_template_for_frame(request,frame)
        if __debug__: print "npt_name = ",npt_name
        if npt_name:
            request.effective_query_extend({'with_template':
                                            npt_name})
        nooron_root.publish(request,frame)

    def npt_for_app_front(app,request,frame):
        print "frame =",frame
        return None

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

