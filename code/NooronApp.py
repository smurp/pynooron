
__version__='$Revision: 1.18 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.18 2002/12/04 19:17:28 smurp Exp $'

#import GW
#from GWApp import GWApp

from pyokbc import *
import NooronRoot
from CachingPipeliningProducer import PipeSection, CachingPipeliningProducer
#from AccessControl import allow_module
#allow_module('pyobkc')


class AbstractApp:
    __allow_access_to_unprotected_subobjects__ = 1
    default_npt_name = "dir_as_html"
    
    def __init__(app,kb):
        app._kb = kb
        goto_kb(kb)

    def get_npt_from_url(app,request):
        query = request.split_query()
        return query.get('with_template')

    def publish(app,request):
        npt_name = app.get_npt_from_url(request) or app.default_npt_name
        request.effective_query_extend({'with_template': npt_name})
        nooron_root.publish(request,app._kb)

    def get_npt_for_self(app,request,frame):
        kb = app._kb
        (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_self',
                                                 number_of_values=1,
                                                 slot_type=Node._all)
        return vals and vals[-1]

class MetaKB(AbstractApp):
    """Lets publish a meta-kb shall we?"""
    default_npt_name = "dir_as_html"    


class NooronApp(AbstractApp):
    """Publish a generic kb generically or a NooronApp kb appropriately."""
    default_npt_name = "kb_as_html"


class GenericFrame(AbstractApp):
    # see http://www.noosphere.org/discuss/zwiki/VariousTemplateUseCases
    default_npt_name = "frame_as_html"
    app = {}
    def publish(app,request,frame_name,npt_name,extensions=[]):
        
        if frame_name == None:
            frame = app._kb
        else:
            (frame,frame_found_p) = frame_name \
                                    and app._kb.get_frame_in_kb(frame_name) \
                                    or (None,None)
            if not frame:
                frame = app._kb

        if npt_name == None:
            npt_name = app.choose_an_npt(request,frame)

        print "\n=====================\n",\
              "publish() npt_name:",npt_name,\
              "for frame:",frame

        cp = CachingPipeliningProducer()
        cp.set_canonical_request(request.uri)
        cp.set_cachedir('/tmp/nooron_cache')

        dotsplit = npt_name.split('.')
        prev_ext = dotsplit[-1]
        extensions.pop(0) # only required so long as okbc_handler prepends npt
        spigot = app.get_pipe_section_for_spigot(prev_ext)
        if spigot:
            cp.append_pipe(spigot)
        for this_ext in extensions:
            pipesection = app.get_pipe_section(from_ext=prev_ext,
                                               to_ext=this_ext)
            prev_ext = this_ext
            cp.append_pipe(pipesection)
        request['Content-Type'] = cp.mimetype()

        cmds = cp.source_and_commands()[1]
        print cp.source_and_commands()
        resp = cmds or 'no commands'
        request.push(resp)
        request.done()

    def get_pipe_section(app,
                         from_ext=None,from_type=None,
                         to_ext=None,to_type=None):
        """Find a frame for a NooronTransformer which goes from
        the from_ situation to the to_ situation.  There are two
        well-know-name forms that this implementation relies on
        (though sufficient information exists on the frames for
        the well-knownedness to merely be for efficiency).
        There are frames like 'FOO_extension' FOO=ps
        There are frames like 'transform_FOO_2_BAR' FOO=ps, BAR=pdf
        They are, respectively the source of mimetypes and commands.
        """
        extension_frame = '%s_extension' % to_ext
        mimetype=get_slot_value(extension_frame,'MimeType')[0]
        transformer_frame = 'transform_%s_2_%s' % (from_ext,to_ext)
        command=get_slot_value(transformer_frame,'LiteralExternalCommand')[0]
        return PipeSection(command=command,
                           extension=to_ext,
                           mimetype=mimetype)

    def get_pipe_section_for_spigot(app,to_ext,producer=None):
        extension_frame = '%s_extension' % to_ext
        mimetype=get_slot_value(extension_frame,'MimeType')[0]        
        return PipeSection(producer=None,
                           extension=to_ext,
                           mimetype=mimetype)
        
        

    def choose_an_npt(app,request,frame):
        return app.get_npt_from_url(request) \
               or app.get_npt_for_subclasses(request,frame) \
               or app.get_npt_for_instances(request,frame) \
               or app.get_npt_for_self(request,frame) \
               or app.get_npt_hardwired(request,frame) \
               or app.default_npt_name
        

    def get_npt_hardwired(app,request,frame):
        kb = app._kb
        if kb == frame:
            return 'kb_as_html'
        else:
            return 'frame_as_html'

    def get_npt_for_subclasses(app,request,frame):
        kb = app._kb
        print "kb is",kb
        if not kb.class_p(frame):
            return None
        (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_subclasses',
                                                 number_of_values=1,
                                                 slot_type=Node._all)
        return vals and vals[0] 

    def get_npt_for_instances(app,request,frame):
        kb = app._kb
        vals = []
        if kb.class_p(frame):
            (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_instances',
                                                     number_of_values=1,
                                                     slot_type=Node._all)
        return vals and vals[0] 

    def get_npt_for_self(app,request,frame):
        kb = app._kb
        (vals,exact_p,more) = kb.get_slot_values(frame,'npt_for_self',
                                                 number_of_values=1,
                                                 slot_type=Node._all)
        return vals and vals[-1] 
