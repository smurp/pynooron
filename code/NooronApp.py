
__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.1 2002/08/07 20:23:41 smurp Exp $'

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
        print "npt_name = ",npt_name
        if npt_name:
            request.effective_query_extend({'with_template':
                                            npt_name})
        NooronRoot.NooronRoot().publish(request,topic_obj)

    def get_template_for_topic(self,request,topic_obj):
        npt_name = None
        query = request.split_query()
        with_template = query.get('with_template')
        if with_template:
            npt_name = with_template
        else:
            clsses = topic_obj.getClasses()
            print "clsses = ",clsses
            for clss in clsses:
                #some = clss.getOccurrences(typ='npt_for_instances')
                some = clss.getOccurrences()
                print str(clss.getBaseNames())," some = ",some
                if some:
                    npt_name = str(some[0][2].getSCR().getUris()[0])
                    break
        return npt_name
