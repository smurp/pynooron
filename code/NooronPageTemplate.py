
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: NooronPageTemplate.py,v 1.2 2002/08/02 18:47:18 smurp Exp $'

import NooronRoot

# PageTemplate Support
import sys
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python/Products')
from PageTemplates.PageTemplate import PageTemplate

#print sys.pwd
#sys.path.append('code')

class NooronPageTemplate(PageTemplate):
    request = None
    obj = None
    
    def __init__(self,request,obj,container):
        self.request = request
        self.obj = obj
        self.container = container
        self.root = NooronRoot.NooronRoot()

    def pt_getContext(self):
        c = {'template': self,
             'here': self.obj,
             'container': self.container,
             'nothing': None,
             'options': {},
             'root': self.root,
             'request': self.request,
             'user': self.request.user(),
             'modules': None,
             }
        return c

