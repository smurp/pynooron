
__version__='$Revision: 1.3 $'[11:-2]
__cvs_id__ ='$Id: NooronPageTemplate.py,v 1.3 2002/08/04 21:43:20 smurp Exp $'

import NooronRoot

import sys
from PageTemplates.PageTemplate import PageTemplate


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

