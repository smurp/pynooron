
__version__='$Revision: 1.17 $'[11:-2]
__cvs_id__ ='$Id: OkbcOperation.py,v 1.17 2003/06/28 21:48:21 smurp Exp $'


SAFETY = 0 # safety off means that OkbcOperation are run when call()ed

if SAFETY:
    print "Notice: OkbcOperation.SAFETY is ON"
else:
    print """
Warning: OkbcOperation.SAFETY is OFF
         Remote users can perform any OKBC operation on
         your running system.  This can be used to create
         instances of
            /know/transformers_ontology/ExternalCommand
         which can be used to compromise system security.
"""

import inspect
from pyokbc import *
import re
import time
import base64


def detail_preprocessor(form,kb,arg):
    """Used by OkbcOperation to obtain a properly constructed detail arg from
    an http form.  The form is in the template put_frame_details.html.  The
    detail argument is used by create-frame and put-frame-details."""
    assert(arg=='details')
    STR = (1,'') # string value expected
    FCT = (2,[]) # facet-spec value expected
    SLT = (3,[]) # slot-spec value expected
    TYP = (4,[]) # list of types
    expect = {':pretty-name':STR,':name':STR,
              ':own-slots':SLT,':template-slots':SLT,
              ':own-facets':FCT, ':template-facets':FCT,}
              #':types': TYP}
    #string_fields = [':pretty-name',':name']
    #slot_spec_fields = [':own-slot',':template-slot']
    #facet_spec_fields = [':own-facets',':template-facets']
    details = {}
    delim = nooron_root.field_path_delim
    for subarg in form.get(arg+delim,[]):
        try:
            def_val = expect[subarg][1]
        except:
            continue
        current_key = arg+delim+subarg
        the_val = form.get(current_key,
                           form.get(current_key+delim,def_val))
        if expect[subarg] == STR:
            if type(the_val) != type(def_val):
                if type(the_val) == type([]) and len(the_val):
                    the_val = the_val[0]
                else:
                    the_val = def_val
        if expect[subarg] == SLT:
            slot_specs = []
            for slot in the_val:
                the_val = form.get(current_key+delim+slot)
                if type(the_val) != type([]):
                    if the_val == None:
                        the_val = []
                    else:
                        the_val = [the_val]
                rng = range(len(the_val))
                rng.reverse()
                for i in rng:
                    if the_val[i] == '':
                        the_val.pop(i)
                slot_spec = [slot]
                slot_spec.extend(the_val)
                slot_specs.append(slot_spec)
            the_val = slot_specs
        if the_val != '':
            details[subarg] = the_val
    return details
put_frame_details.http_argument_preprocessors = {'details':
                                                 detail_preprocessor}


def make_good_name(form,kb,arg):
    """If name is absent, then make it by compressing the pretty_name
    into a WikiWord.  If pretty_name is absent or unsuitable then make
    a name automatically from the timestamp which is then base64
    encoded for size (and /+= are suppressed).  Should really include
    the IP or something too."""
    assert(arg=='name')
    the_name = form.get('name','')
    pretty_name = ''
    if the_name in ('',None,['']):
        the_name = WikiWord.make_wiki_word(form.get('pretty_name',[''])[0])
    elif type(the_name) == type([]):
        the_name = the_name[0]
    if kb:
        if frame_in_kb_p(the_name,kb=kb):
            the_name = ''
    if the_name == '':
        # the time to hundredths of seconds
        the_bin = long(time.time() * 100.0)
        # express as 8 bit string
        the_parts = []
        while the_bin > 0:
            the_bin,part = divmod(the_bin,256)
            the_parts.append(chr(part))
        the_string = string.join(the_parts,'')
        b64 = base64.encodestring(the_string)
        # remove =, / and +
        b64good = string.replace(b64,'=','')
        b64good = string.replace(b64good,'/','')
        b64good = string.replace(b64good,'+','')        
        # make sure they don't accidentally look like words
        b64good = 'ZQ'+string.replace(b64good,'+','') 
        the_name = b64good[:-1] # loose the trailing newline
    #print "calling name_automatically_if_absent returns",the_name
    return the_name
create_individual.http_argument_preprocessors = {'name':
                                                 make_good_name}


def build_slot_specs(own_or_template_slots,form):
    """Accumulate own_slots or template_slots into a slot_specs value.
    own_or_template_slots is either 'own_slots' or 'template_slots'"""
    my_slots = form[own_or_template_slots] or []
    retval = []
    for slot_name in my_slots:
        retval.append([slot_name]+list(form.get(slot_name,[])))
    return retval

def convert_query_to_okbc_args_and_kwargs(func,form,kb):
    (args,varargs,varkw,defaults) = inspect.getargspec(func)
    http_argument_preprocessors = func.__dict__.get('http_argument_preprocessors',{})
    last_positional_idx = len(args) - len(defaults) - 1 
    #print "last_positional_idx",last_positional_idx
    posargs = []
    kwargs  = {}
    for argidx in range(len(args)):
        ispositional = argidx <= last_positional_idx
        arg = args[argidx]
        #print 'argidx',argidx,'arg',arg,'ispositional',ispositional
        kw_val = pos_val = None        
        del kw_val, pos_val
        if arg in form.keys():
            val = form.get(arg,[])
            if ispositional:
                pos_val = len(val)==1 and val[0] or val
            else:
                if arg in ['own_slots','template_slots']:
                    kw_val = build_slot_specs(arg,form)
                elif arg == 'pretty_name':
                    kw_val = len(val) and val[0]
                elif arg == 'kb':
                    kw_val = len(val) and val[0] or op._kb
                else:
                    kw_val = val
        else:
            if arg == 'kb':
                #print "type(kb) =",type(kb),kb
                if type(kb) == type([]):
                    kb = kb[0]
                kw_val = pos_val = kb

        if http_argument_preprocessors.has_key(arg):
            pos_val = http_argument_preprocessors[arg](form,kb,arg)
            
        if ispositional and 'pos_val' in dir():
            posargs.append(pos_val)
        if not ispositional and 'kw_val' in dir():
            kwargs[arg] = kw_val

    #print 'posargs',posargs,'kwargs',kwargs
    return (posargs,kwargs)

class OkbcOperation:
    def __init__(op,func,request,kb=None,frame=None):
        op._func = func
        op._request = request
        op._kb = kb
        op._frame = frame

    def get_kb_to_write_to(op):
        """
* have instances written to nooron_app_data KBs, but how?
** Have the original actions specify the target kb explicitly.
** Have the nooron_app_instance delegate creation to assoc. *_data.
** Have NooronApp do the delegating.
** Have knowledge trigger the delegation
*** Some template slot on nooron_app_instance such as:
      delegate_writing_to_data_kb
**** No! No! We already know that we want to do this
** What we need to handle this in a more generic fashion.
** What are the issues?
*** Sometimes classes need to have their instances stored in particular KBs.
**** This arises when multiple _ontology and _data kbs are in use.
*** Sometimes users want to store their work other than in the default place.
**** e.g. When they want to make private notes or modifications.
**** e.g. When the source of the rest of the data is read-only.
** What are the knowledge-driven ways to do these sorts of things?
*** Have slots on kbs indicating the classes they can store instances of.
*** Have a frame 'STORAGE_PREFERENCES' which has slots which tell things where to go.
*** Have slots on the nooron_app_instance kb itself which tell things where to go.
*** Have slots on :CLASS which guide storage policies.  
Generally overridden on particular classes.  The problem is that each class 
needs to be handled separately (unless some wonderful slot type can 
simplify this.)  :SAME-VALUES with a slot chain might prove useful.
** What is the simplest solution for now?
*** Have OkbcOperation detect attempts to create in nooron_app_instances and
replace them with creation attempts in appropriate _data kbs.
 """
        # FIXME get_kb_to_write_to is very crude
        if instance_of_p(op._kb,'nooron_app_instance',kb=op._kb):
            parents =  get_kb_direct_parents(kb=op._kb)
            for parent in parents:
                if instance_of_p(parent,'nooron_app_data',kb=op._kb)[0]:
                    return parent
        return op._kb
        
    def get_args_and_kwargs(op):
        #print "op._func", op._func
        (args,varargs,varkw,defaults) = inspect.getargspec(op._func)
        #print len(args),len(defaults)
        #print "getargs",inspect.getargs(op._func.func_code)
        #print "getargspec",inspect.getargspec(op._func)
        #kwargs = op._request.form()
        largs = []
        kwargs = {}
        #write_to_kb = op.get_kb_to_write_to()
        write_to_kb = op._kb
        return convert_query_to_okbc_args_and_kwargs(op._func,
                                                     op._request.form(),
                                                     write_to_kb)

    def get_redirect(op):
        return op._request.form().get('OnSuccessRedirectTo',[None])[0]
    
    def call(op):
        accepted_p = None
        if SAFETY:
            res = 'OkbcOperations are not permitted because SAFETY is ON'
        else:
            (posargs,kwargs) = op.get_args_and_kwargs()
            #print "callDump",posargs,kwargs
            accepted_p = 1
            res = apply(op._func,posargs,kwargs)
        return (accepted_p,res)


class AuthorizedOkbcOperation(OkbcOperation):
    def call(op,security_engine):
        res = None
        if SAFETY:
            res = 'OkbcOperations are not permitted because SAFETY is ON'
        if security_engine:
            denied = security_engine.denied_p(op)
        else:
            denied = None
        if not denied:
            (posargs,kwargs) = op.get_args_and_kwargs()
            res = apply(op._func,posargs,kwargs)
        else:
            res = denied
        accepted_p = not denied        
        return (accepted_p,res)
