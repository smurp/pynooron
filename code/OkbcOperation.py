
__version__='$Revision: 1.4 $'[11:-2]
__cvs_id__ ='$Id: OkbcOperation.py,v 1.4 2003/02/26 10:42:42 smurp Exp $'


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
    last_positional_idx = len(args) - len(defaults) - 1 
    #print "last_positional_idx",last_positional_idx
    posargs = []
    kwargs  = {}
    for argidx in range(len(args)):
        ispositional = argidx <= last_positional_idx
        arg = args[argidx]
        #print 'argidx',argidx,'arg',arg,'ispositional',ispositional
        if arg in form.keys():
            val = form.get(arg,[])
            if ispositional:
                posargs.append(len(val)==1 and val[0] or val)
            else:
                if arg in ['own_slots','template_slots']:
                    kwargs[arg] = build_slot_specs(arg,form)
                elif arg == 'pretty_name':
                    kwargs[arg] = len(val) and val[0]
                else:
                    kwargs[arg] = val
        else:
            if arg == 'kb':
                if ispositional:
                    posargs.append(kb)
                else:
                    kwargs[arg] = kb
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
        write_to_kb = op.get_kb_to_write_to()
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
