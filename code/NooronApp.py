
__version__='$Revision: 1.12 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.12 2002/11/11 22:48:50 smurp Exp $'

#import GW
#from GWApp import GWApp

from pyokbc import *
import NooronRoot

#from AccessControl import allow_module
#allow_module('pyobkc')


class AbstractApp:
    __allow_access_to_unprotected_subobjects__ = 1
    default_npt_name = "dir_as_html"
    
    def __init__(app,kb):
        app._kb = kb
        goto_kb(kb)

    def publish(app,request):
        """Ultimately does a nooron_root.publish(request,sumut)."""
        nooron_root.publish(request,object)

    def get_npt_from_url(app,request):
        query = request.split_query()
        return query.get('with_template')

    def publish(app,request):
        npt_name = app.get_npt_from_url(request) or app.default_npt_name
        request.effective_query_extend({'with_template': npt_name})
        nooron_root.publish(request,app._kb)


class MetaKB(AbstractApp):
    """Lets publish a meta-kb shall we?"""
    default_npt_name = "dir_as_html"    


class NooronApp(AbstractApp):
    """Publish a generic kb generically or a NooronApp kb appropriately."""
    default_npt_name = "kb_as_html"


class GenericFrame(AbstractApp):
    # see http://www.noosphere.org/discuss/zwiki/VariousTemplateUseCases
    default_npt_name = "frame_as_html"
    def publish(app,request,frame_name):
        (frame,frame_found_p) = frame_name \
                                and app._kb.get_frame_in_kb(frame_name) \
                                or (None,None)
        if not frame_found_p:
            NooronApp(app._kb).publish(request)
            return
        print "frame =",frame
        npt_name = app.get_npt_from_url(request) \
                   or app.get_npt_for_subclasses(request,frame) \
                   or app.get_npt_for_instances(request,frame) \
                   or app.get_npt_for_self(request,frame) \
                   or app.default_npt_name
        print "=====================\n",\
              "publish() npt_name:",npt_name,\
              "for frame:",frame
        request.effective_query_extend({'with_template': npt_name})
        nooron_root.publish(request,frame)

    def get_npt_for_subclasses(app,request,frame):
        kb = app._kb
        if not kb.class_p(frame):
            return None
        (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_subclasses',
                                                 number_of_values=1,
                                                 slot_type=Node._all)
        return vals and vals[0] 


    def get_npt_for_instances(app,request,frame):
        kb = app._kb
        (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_instances',
                                                 number_of_values=1,
                                                 slot_type=Node._all)
        return vals and vals[0] 

    def get_npt_for_self(app,request,frame):
        kb = app._kb
        (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_self',
                                                 number_of_values=1,
                                                 slot_type=Node._all)
        return vals and vals[0] 
