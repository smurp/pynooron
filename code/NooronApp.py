
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.2 2002/08/12 22:48:33 smurp Exp $'

import GW
from GWApp import GWApp

import NooronRoot

class NooronApp(GWApp):
    def isNooronApp(self):
        return 0

# see http://www.noosphere.org/discuss/zwiki/VariousTemplateUseCases
    def publish(self,request,topic_obj):
        args = {}
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

