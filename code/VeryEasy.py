
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: VeryEasy.py,v 1.2 2002/08/13 06:22:13 smurp Exp $'

"""A wrapper for C objects that is acceptable to the security machinery."""

class VeryEasy:
    
    def __init__(self,wrappee):
        self.__wrappee = wrappee

    def __getattr__(self,key):
        #print "__get_attr__",key
        if str(key) == '__allow_access_to_unprotected_subobjects__':
            return 1
        return getattr(self.__wrappee,key)
