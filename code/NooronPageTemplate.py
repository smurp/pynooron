
__version__='$Revision: 1.11 $'[11:-2]
__cvs_id__ ='$Id: NooronPageTemplate.py,v 1.11 2002/11/18 23:45:13 smurp Exp $'

SAFETY = 1 # safety off means that python in NPTs is omnipotent

import NooronRoot

import sys
from PageTemplates.PageTemplate import PageTemplate, PTRuntimeError
from TAL.TALInterpreter import TALInterpreter
from TAL.TALGenerator import TALGenerator
from TAL.HTMLTALParser import HTMLTALParser
from TAL.TALParser import TALParser

from cStringIO import StringIO
#Z_DEBUG_MODE = 0

from pyokbc import *

import inspect

okbc_functions={}
for i in inspect.getmembers(Funcs,inspect.isfunction):
    okbc_functions[i[0]]=i[1]

if SAFETY: #safe
    print "Relax: NPT SAFETY is ON"
    from PageTemplates.ZRPythonExpr import PythonExpr, \
         _SecureModuleImporter,\
         call_with_ns
    from SafeExpressions import getEngine
else:
    print "Warning: NPT SAFETY is OFF"
    from PageTemplates.PythonExpr import getSecurityManager, PythonExpr
    from PageTemplates.Expressions import getEngine
    def call_with_ns(f, ns, arg=1):
        if arg==2:
            return f(None, ns)
        else:
            return f(ns)

    class _SecureModuleImporter:
        """Simple version of the importer for use with trusted code."""
        __allow_access_to_unprotected_subobjects__ = 1
        def __getitem__(self, module):
            __import__(module)
            return sys.modules[module]

SecureModuleImporter = _SecureModuleImporter()

class NooronPageTemplate(PageTemplate):
    request = None
    obj = None
    
    def __init__(self,request,obj,container):
        self.request = request
        self.obj = obj
        self.container = container
        self.root = nooron_root

    def pt_getContext(self):
        c = {'template': self,
             'here': self.obj,
             'this': self.obj,             
             'this_kb':current_kb(),
             'container': self.container,
             'nothing': None,
             'options': {},
             'root': self.root,
             'request': self.request,
             #'user': self.request.user(), # FIXME why is user absent?
             'modules': SecureModuleImporter,
             'Node': Node
             }
        #print "context:",c
        return c

    def pt_render(self, source=0, extra_context={}):
        """Render this Page Template"""
        if self._v_errors:
            print "type(self._v_errors)=",type(self._v_errors)
            print self._v_errors
            raise PTRuntimeError, 'Page Template %s has errors.' % self.id
        output = StringIO()
        c = self.pt_getContext()
        c.update(extra_context)
        c.update(okbc_functions)
        c.update(Node.kwargs)
        #if Z_DEBUG_MODE:
        #    __traceback_info__ = pprint.pformat(c)
        #print "_v_program =",self._v_program
        #print "getEngine().getContext(c) =",getEngine().getContext(c)
        TALInterpreter(self._v_program, self._v_macros,
                       getEngine().getContext(c),
                       output,
                       tal=not source, strictinsert=0)()
        return output.getvalue()

    def _cook(self):
        """Compile the TAL and METAL statments.

        A Page Template must always be cooked, and cooking must not
        fail due to user input.
        """
        if self.html():
            gen = TALGenerator(getEngine(), xml=0)
            parser = HTMLTALParser(gen)
        else:
            gen = TALGenerator(getEngine())
            parser = TALParser(gen)

        self._v_errors = ()
        try:
            parser.parseString(self._text)
            self._v_program, self._v_macros = parser.getCode()
        except:
            self._v_errors = ["Compilation failed",
                              "%s: %s" % sys.exc_info()[:2]]
        self._v_warnings = parser.getWarnings()

