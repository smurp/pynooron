
__version__='$Revision: 1.3 $'[11:-2]
__cvs_id__ ='$Id: OkbcOperation.py,v 1.3 2003/02/26 10:16:38 smurp Exp $'


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
