
"""A wrapper for C objects that is acceptable to the security machinery."""

class VeryEasy:
    
    def __init__(self,wrappee):
        self.__wrappee = wrappee

    def __getattr__(self,key):
        #print "__get_attr__",key
        if str(key) == '__allow_access_to_unprotected_subobjects__':
            return 1
        return getattr(self.__wrappee,key)
