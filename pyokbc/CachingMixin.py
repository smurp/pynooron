
_version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: CachingMixin.py,v 1.2 2003/01/20 14:52:29 smurp Exp $'


from __future__ import nested_scopes
import string
from Funcs import okbc_readonly_kb_functions


def make_a_wrapper(kb,wrapped_method,name_of_method):
    """Return the wrapped_method with a caching method around it."""
    def caching_wrapper(*args,**kwargs):
        allow_caching = kb.allow_caching_p()
        if allow_caching:
            cache_key = name_of_method + " " + \
                        string.join(map(str,args),'|')
            kwargs_keys = kwargs.keys()
            kwargs_keys.sort()
            for kw in kwargs_keys:
                cache_key = cache_key + '|' + str(kwargs[kw])
            if kb._cache.has_key(cache_key):
                #print "CACHE HIT",cache_key
                return kb._cache[cache_key]
        args = [kb] + list(args)
        retval = apply(wrapped_method,args,kwargs)
        if allow_caching: kb._cache[cache_key] = retval
        return retval
    return caching_wrapper

def make_a_procedure_wrapper(kb,wrapped_method,name_of_method):
    """Return the wrapped_method with a caching method around it."""
    def procedure_caching_wrapper(procedure,arguments=None):
#    def procedure_caching_wrapper(*args,**kwargs):
        #procedure = args[0]
        #arguments = args[1]
        allow_caching = hasattr(procedure,'read') \
                        and getattr(procedure,'read') \
                        and kb.allow_caching_p()
        if allow_caching:
            cache_key = 'call_procedure ' + procedure.func_name + \
                        string.join(map(str,arguments or []),'|')
            if kb._cache.has_key(cache_key):
                print "CACHE HIT",cache_key            
                return kb._cache[cache_key]
        retval = wrapped_method(kb,procedure,arguments)
        #retval = apply(wrapped_method,args,kwargs)        
        if allow_caching:
            kb._cache[cache_key] = retval
        return retval
    return procedure_caching_wrapper

class CachingMixin:
    """A class which when mixed into a KB wraps OKBC read operations with
    caching abilities."""
    def __init__(kb):
        """For each readonly Func which has an equivalent in the
        class I am being mixed into, create a method in me which
        performs caching and, failing to find a cached value, calls
        the old method."""
        for fname in okbc_readonly_kb_functions:
            if fname == 'call_procedure':
                kb_meth = getattr(kb,fname)
                kb.__dict__[fname] = make_a_procedure_wrapper(kb,kb_meth.im_func,fname)
            else:
                if hasattr(kb,fname):
                    kb_meth = getattr(kb,fname)
                    kb.__dict__[fname] = make_a_wrapper(kb,kb_meth.im_func,fname)
                else:
                    continue