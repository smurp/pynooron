
__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: inspect_module.py,v 1.1 2002/07/18 20:44:36 smurp Exp $'

"""
Return the classes in module and only in module.

"""

import types

def _values_recurse(dict,array):
    for (k,v) in dict.items():
        if type(v) == type({}):
            _values_recurse(v,array)
        else:
            array.append(v)

def classes_in_module(module):
    dict = _classes_in_module_recurse(module,'--')
    array = []
    _values_recurse(dict,array)
    return array

def _classes_in_module_recurse(module,prefix):
    retval = {}
    for name in module.__dict__.keys():
        memb = module.__dict__[name]
        if name[0] == '_':
            continue
        if isinstance(memb,types.ClassType):
            #print prefix + "class", name
            retval[name] = memb
        elif isinstance(memb,types.ModuleType):
            if memb.__name__ == module.__name__+"."+name:
                #print prefix + "module", name
                retval[name] = _classes_in_module_recurse(memb,prefix + "--")
            else:
                pass
                # these are modules which live somewhere else
                #print prefix + "imports module", name, memb.__name__, module.__name__
    return retval
