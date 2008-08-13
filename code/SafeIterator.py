
"""Safe Iterator

A TALES Iterator with the ability to use first() and last() on
subpaths of elements and which uses the SafeExpressions mechanisms.
"""

__version__='$Revision: 1.2 $'[11:-2]

import ZopePageTemplates
from SafeExpressions import restrictedTraverse, Undefs, getSecurityManager
from string import split

class Iterator(ZopePageTemplates.TALES.Iterator):
    def __bobo_traverse__(self, REQUEST, name):
        if name in ('first', 'last'):
            path = REQUEST['TraversalRequestNameStack']
            names = list(path)
            names.reverse()
            path[:] = [tuple(names)]
        return getattr(self, name)

    def same_part(self, name, ob1, ob2):
        if name is None:
            return ob1 == ob2
        if isinstance(name, type('')):
            name = split(name, '/')
        name = filter(None, name)
        securityManager = getSecurityManager()
        try:
            ob1 = restrictedTraverse(ob1, name, securityManager)
            ob2 = restrictedTraverse(ob2, name, securityManager)
        except Undefs:
            return 0
        return ob1 == ob2
