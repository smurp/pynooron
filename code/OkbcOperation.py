

__version__='$Revision: 1.7 $'[11:-2]
__cvs_id__ ='$Id: OkbcOperation.py,v 1.7 2003/03/28 07:31:46 smurp Exp $'


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
                slot_spec = [slot]
                slot_spec.extend(form.get(current_key+delim+slot))
                slot_specs.append(slot_spec)
            the_val = slot_specs
        details[subarg] = the_val
    return details
put_frame_details.http_argument_preprocessors = {'details':detail_preprocessor}


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
    def call(op):
        if SAFETY:
            return 'OkbcOperations are not permitted because SAFETY is ON'
        else:
            (posargs,kwargs) = op.get_args_and_kwargs()
            print "callDump",posargs,kwargs
            return apply(op._func,posargs,kwargs)


class AuthorizedOkbcOperation(OkbcOperation):
    def call(op,security_engine):
        if SAFETY:
            return 'OkbcOperations are not permitted because SAFETY is ON'
        denied = security_engine.denied_p(op)
        if not denied:
            (posargs,kwargs) = op.get_args_and_kwargs()
            #print "callDump",posargs,kwargs
            return apply(op._func,posargs,kwargs)
        else:
            return denied
        
class IPListSecurityEngine:
    """IPListSecurityEngine allows or denies listed IPs or denies everybody.

    usage:
      # allow only listed IPs deny everybody else
      IPListSecurityEngine(allow=['1.1.1.17'],deny=1)
      
      # deny listed IPs, allow everybody else
      IPListSecurityEngine(deny=['1.1.1.17'],allow=1)
      
      # deny everybody, tell them why
      IPListSecurityEngine(deny=1,message="On hiatus!")
    """
    def __init__(self,allow=[],deny=[],
                 message='Not authorized to perform that operation.',
                 chain = None):
        self._allow   = allow
        self._deny    = deny
        self._message = message
        self._chain   = chain

    def denied_p(self,op):
        addr = op._request.channel.addr[0]
        #print ">'%s'<" % addr, self._allow
        #if self._allow == 1 or addr in self._allow:
        the_guy_is_bad = type(self._deny) == type([]) and addr in self._deny
        the_guy_is_good = type(self._allow) == type([]) and addr in self._allow
        if the_guy_is_bad:
            return self._message
        if the_guy_is_good:
            return None
        
        if self._allow == 1:
            return None
        if self._deny == 1:
            return self._message
        
        if self._chain:
            return self._chain.denied_p(op)
        
        return None  # allow ALL otherwise
