
__version__='$Revision: 1.26 $'[11:-2]
__cvs_id__ ='$Id: NooronApp.py,v 1.26 2003/01/07 18:35:23 smurp Exp $'


from pyokbc import *
import NooronRoot
from CachingPipeliningProducer import PipeSection, CachingPipeliningProducer
#from AccessControl import allow_module
#allow_module('pyobkc')
import medusa.producers
import popen2
from OkbcOperation import OkbcOperation

class AbstractApp:
    __allow_access_to_unprotected_subobjects__ = 1
    default_npt_name = None
    
    def __init__(app,kb):
        app._kb = kb
        goto_kb(kb)

    def get_npt_from_url(app,request):
        query = request.split_query()
        return query.get('with_template')


class GenericFrame(AbstractApp):
    # see http://www.noosphere.org/discuss/zwiki/VariousTemplateUseCases
    default_npt_name = "frame_as_html"
    app = {}
    def publish(app,request,frame_name,npt_name,extensions=[]):
        if frame_name == None:
            frame = app._kb
        else:
            (frame,frame_found_p) = \
                  frame_name \
                  and app._kb.get_frame_in_kb(frame_name) or (None,None)
            if not frame:
                npt_name = 'frame_not_found.html'
                frame = frame_name


        if npt_name in okbc_functions.keys():
            #print "header    ",request.header
            #print "split_uri ",request.split_uri()
            #print npt_name, "is an OKBC Func"
            a_func = okbc_functions[npt_name]
            op = OkbcOperation(a_func,request,kb=app._kb, frame=frame)
            #print "args and kwargs",op.get_args_and_kwargs()
            operation_result = op.call()
            print operation_result
            npt_name = 'show_form.html'



        if npt_name == None:
            npt_name = app.choose_an_npt(request,frame)

        template = nooron_root.template_root().obtain(npt_name,
                                                      request=request,
                                                      obj=frame)
        template.title = npt_name
        tp = template_producer(template,frame)

        dotsplit = npt_name.split('.')
        prev_ext = dotsplit[-1]
        spigot = app.get_pipe_section_for_spigot(prev_ext,
                                                 producer = tp)

        app.calc_canonical_request(request,frame,npt_name,template)
        canonical_request = request.canonical_request()
        #print "canonical_request",canonical_request
        
        cp = CachingPipeliningProducer()
        cp.set_canonical_request(canonical_request)
        cp.set_cachedir('/tmp/nooron_cache')
        
        if spigot:
            cp.append_pipe(spigot)
        for this_ext in extensions:
            pipesection = app.get_pipe_section(from_ext=prev_ext,
                                               to_ext=this_ext)
            prev_ext = this_ext
            cp.append_pipe(pipesection)

        request['Content-Type'] = cp.mimetype()
        #print         request['Content-Type'] 

        #cmds = cp.source_and_commands()[1]
        (src_prod,cmds) = cp.producer_and_commands()
        #print "==========\n",src_prod,cmds,"\n=========="
        if src_prod:
            (fout,fin)=popen2.popen2(cmds,1<<16)
            fin.write(src_prod.more())
            fin.flush()
            fin.close()
            #src_prod.close()
            final_producer = medusa.producers.file_producer(fout)
        else:
            final_producer = \
                   medusa.producers.file_producer(os.popen(cmds,'r'))

        #print "base_request",request.base_request()
        request.push(final_producer)        
        #request.push(dummy_producer())

        #prod = medusa.producers.file_producer(os.popen(cmds,'r'))
        #request.push(prod)
        request.done()

    def calc_canonical_request(app,request,frame,npt_name,template):
        """The canonical request is meant to unambiguously identify the
        state of the system in such a way that the CR will only differ if
        something has happened to either the knowledge, the logic, or
        the presentation such that any cached results may be invalid.
        Initially, the canonical_request will be consist of the following
        values on succeeding lines:
          the base_request,
          the most recent change_time of all the parent_kbs
          the most recent change_time of all involved templates
          some indication of involved user preferences """
        app.calc_base_request(request,frame,npt_name)
        # FIXME must add change_times for parent_kbs and templates
        request.set_canonical_request("%s\nkb_mtime=%s\ngarment_mtime=%s\n%s\n"%(
            request.base_request(),
            str(app._kb.get_kb_parents_maximum_mtime()),
            str(template._stats['MTIME']),
            str(request.split_uri()[2])
            ))

    def calc_base_request(app,request,frame,npt_name):
        """
        The base request is the path the user could (or might) have
        visited to be explicit about which GARMENT to use.  If the
        actual_request is not a base_request (bacause it does not specify
        a garment) then some algorithm (such
        as pick the first possible garment which produces .html) is
        used to determine the base_request.  Notice that no transforming
        or encoding extensions (such as .ps, .pdf, .gz) are included.
        THING__GARMENT  eg /know/nooron_faq/faq__details.html
        """
        request.set_base_request(request.object_request() + '__' + npt_name)

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
        return PipeSection(producer=producer,
                           extension=to_ext,
                           mimetype=mimetype)

    def choose_an_npt(app,request,frame):
        return app.get_npt_from_url(request) \
               or app.get_nearest_preferred_npt_for_self(request,frame) \
               or app.get_npt_for_instances(request,frame) \
               or app.get_npt_for_self(request,frame) \
               or app.get_npt_hardwired(request,frame) \
               or app.default_npt_name

    def get_npt_hardwired(app,request,frame):
        kb = app._kb
        if kb == frame:
            return 'kb.html'
        else:
            return 'frame.html'

    def get_nearest_preferred_npt_for_self(app,request,frame,prefer=".html"):
        """Return the first garment listed as npt_for_self on one of
        the direct types of frame."""
        kb = app._kb
        direct_types = list(kb.get_instance_types(frame,
                                             inference_level=Node._direct)[0])
        vals = []
        chosen_garmie = None
        while not chosen_garmie and direct_types:
            dtype = direct_types.pop(0)
            (vals,exact_p,more) = kb.get_slot_values(dtype,'npt_for_self',
                                                     number_of_values=1,
                                                     inference_level = Node._direct,
                                                     slot_type=Node._template)
            for garmie in vals:
                if not prefer or \
                   garmie.find(prefer) == len(garmie) - len(prefer):
                    chosen_garmie = garmie
                    break
        return chosen_garmie

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

class dummy_producer:
    def more(self):
        if not self.__dict__.get('_done') :
            self._done = 1
            return "This is just great\n"
        else:
            return ''

class template_producer:
    def __init__(self,template,content):
        self._template = template
        self._content = content
    def more(self):
        if not self.__dict__.get('_done') :
            self._done = 1
            return self._template(content=self._content)
        else:
            return ''

        
