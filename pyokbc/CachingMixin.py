
_version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: CachingMixin.py,v 1.1 2002/12/16 21:00:10 smurp Exp $'


from __future__ import nested_scopes
import string
from Funcs import okbc_readonly_kb_functions


def make_a_wrapper(kb,wrapped_method,name_of_method):
    def caching_wrapper(*args,**kwargs):
        if kb.allow_caching_p():
            cache_key = name_of_method + " " + \
                        string.join(map(str,args),'|')
            kwargs_keys = kwargs.keys()
            kwargs_keys.sort()
            for kw in kwargs_keys:
                cache_key = cache_key + '|' + str(kwargs[kw])
            #print cache_key
            #if cache_key[-1] in ['1','0']:
            #    print "  ",args,kwargs
            if kb._cache.has_key(cache_key):
                #print "CACHE HIT",cache_key
                return kb._cache[cache_key]
        #args = tuple(kb,args)
        #print "kb = ",kb,"func =",name_of_method,"args =",args,"kwargs =",kwargs
        args = [kb] + list(args)
        #print args
        retval = apply(wrapped_method,args,kwargs)
        if kb.allow_caching_p(): kb._cache[cache_key] = retval
        return retval
    return caching_wrapper

class CachingMixin:
    """A class which when mixed into a KB wraps OKBC read operations with
    caching abilities."""
    def __init__(kb):
        """For each readonly Func which has an equivalent in the
        class I am being mixed into, create a method in me which
        performs caching and, failing to find a cached value, calls
        the old method."""
        #return
        #print kb.__class__.__module__
        #print kb.__class__.__dict__
        for fname in okbc_readonly_kb_functions:
            if hasattr(kb,fname):
                kb_meth = getattr(kb,fname)
                #print "wrapping ",fname,"in",kb
                kb.__dict__[fname] = make_a_wrapper(kb,kb_meth.im_func,fname)
            else:
                #print "missing ",fname,"in",kb
                continue
