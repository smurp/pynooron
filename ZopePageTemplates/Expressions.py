##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Page Template Expression Engine

Page Template-specific implementation of TALES, with handlers
for Python expressions, string literals, and paths.
"""

__version__='$Revision: 1.2 $'[11:-2]

import re, sys
from TALES import Engine, CompilerError, _valid_name, NAME_RE, \
     Undefined, Default, _parse_expr

_engine = None
def getEngine():
    global _engine
    if _engine is None:
        from PathIterator import Iterator
        _engine = Engine(Iterator)
        installHandlers(_engine)
    return _engine

def installHandlers(engine):
    reg = engine.registerType
    pe = PathExpr
    for pt in ('standard', 'path', 'exists', 'nocall'):
        reg(pt, pe)
    reg('string', StringExpr)
    reg('python', PythonExpr)
    reg('not', NotExpr)
    reg('defer', DeferExpr)

from PythonExpr import getSecurityManager, PythonExpr
try:
    from zExceptions import Unauthorized
except ImportError:
    Unauthorized = "Unauthorized"
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

Undefs = (Undefined, AttributeError, KeyError,
          TypeError, IndexError, Unauthorized)

def render(ob, ns):
    """
    Calls the object, possibly a document template, or just returns it if
    not callable.  (From DT_Util.py)
    """
    if hasattr(ob, '__render_with_namespace__'):
        ob = call_with_ns(ob.__render_with_namespace__, ns)
    else:
        base = ob
        if callable(base):
            try:
                if getattr(base, 'isDocTemp', 0):
                    ob = call_with_ns(ob, ns, 2)
                else:
                    ob = ob()
            except AttributeError, n:
                if str(n) != '__call__':
                    raise
    return ob

class SubPathExpr:
    def __init__(self, path):
        self._path = path = path.strip().split('/')
        self._base = base = path.pop(0)
        if not _valid_name(base):
            raise CompilerError, 'Invalid variable name "%s"' % base
        # Parse path
        self._dp = dp = []
        for i in range(len(path)):
            e = path[i]
            if e[:1] == '?' and _valid_name(e[1:]):
                dp.append((i, e[1:]))
        dp.reverse()

    def _eval(self, econtext,
              list=list, isinstance=isinstance, StringType=type('')):
        vars = econtext.vars
        path = self._path
        if self._dp:
            path = list(path) # Copy!
            for i, varname in self._dp:
                val = vars[varname]
                if isinstance(val, StringType):
                    path[i] = val
                else:
                    # If the value isn't a string, assume it's a sequence
                    # of path names.
                    path[i:i+1] = list(val)
        __traceback_info__ = base = self._base
        if base == 'CONTEXTS':
            ob = econtext.contexts
        else:
            ob = vars[base]
        if isinstance(ob, DeferWrapper):
            ob = ob()
        if path:
            ob = restrictedTraverse(ob, path, getSecurityManager())
        return ob

class PathExpr:
    def __init__(self, name, expr, engine):
        self._s = expr
        self._name = name
        self._hybrid = 0
        paths = expr.split('|')
        self._subexprs = []
        add = self._subexprs.append
        for i in range(len(paths)):
            path = paths[i].lstrip()
            if _parse_expr(path):
                # This part is the start of another expression type,
                # so glue it back together and compile it.
                add(engine.compile(('|'.join(paths[i:]).lstrip())))
                self._hybrid = 1
                break
            add(SubPathExpr(path)._eval)

    def _exists(self, econtext):
        for expr in self._subexprs:
            try:
                expr(econtext)
            except Undefs:
                pass
            else:
                return 1
        return 0

    def _eval(self, econtext,
              isinstance=isinstance, StringType=type(''), render=render):
        for expr in self._subexprs[:-1]:
            # Try all but the last subexpression, skipping undefined ones.
            try:
                ob = expr(econtext)
            except Undefs:
                pass
            else:
                break
        else:
            # On the last subexpression allow exceptions through, and
            # don't autocall if the expression was not a subpath.
            ob = self._subexprs[-1](econtext)
            if self._hybrid:
                return ob

        if self._name == 'nocall' or isinstance(ob, StringType):
            return ob
        # Return the rendered object
        return render(ob, econtext.vars)

    def __call__(self, econtext):
        if self._name == 'exists':
            return self._exists(econtext)
        return self._eval(econtext)

    def __str__(self):
        return '%s expression %s' % (self._name, `self._s`)

    def __repr__(self):
        return '%s:%s' % (self._name, `self._s`)


_interp = re.compile(r'\$(%(n)s)|\${(%(n)s(?:/[^}]*)*)}' % {'n': NAME_RE})

class StringExpr:
    def __init__(self, name, expr, engine):
        self._s = expr
        if '%' in expr:
            expr = expr.replace('%', '%%')
        self._vars = vars = []
        if '$' in expr:
            parts = []
            for exp in expr.split('$$'):
                if parts: parts.append('$')
                m = _interp.search(exp)
                while m is not None:
                    parts.append(exp[:m.start()])
                    parts.append('%s')
                    vars.append(PathExpr('path', m.group(1) or m.group(2),
                                         engine))
                    exp = exp[m.end():]
                    m = _interp.search(exp)
                if '$' in exp:
                    raise CompilerError, (
                        '$ must be doubled or followed by a simple path')
                parts.append(exp)
            expr = ''.join(parts)
        self._expr = expr

    def __call__(self, econtext):
        vvals = []
        for var in self._vars:
            v = var(econtext)
            # I hope this isn't in use anymore.
            ## if isinstance(v, Exception):
            ##     raise v
            vvals.append(v)
        return self._expr % tuple(vvals)

    def __str__(self):
        return 'string expression %s' % `self._s`

    def __repr__(self):
        return 'string:%s' % `self._s`

class NotExpr:
    def __init__(self, name, expr, compiler):
        self._s = expr = expr.lstrip()
        self._c = compiler.compile(expr)

    def __call__(self, econtext):
        # We use the (not x) and 1 or 0 formulation to avoid changing
        # the representation of the result in Python 2.3, where the
        # result of "not" becomes an instance of bool.
        return (not econtext.evaluateBoolean(self._c)) and 1 or 0

    def __repr__(self):
        return 'not:%s' % `self._s`

class DeferWrapper:
    def __init__(self, expr, econtext):
        self._expr = expr
        self._econtext = econtext

    def __str__(self):
        return str(self())

    def __call__(self):
        return self._expr(self._econtext)

class DeferExpr:
    def __init__(self, name, expr, compiler):
        self._s = expr = expr.lstrip()
        self._c = compiler.compile(expr)

    def __call__(self, econtext):
        return DeferWrapper(self._c, econtext)

    def __repr__(self):
        return 'defer:%s' % `self._s`

class TraversalError:
    def __init__(self, path, name):
        self.path = path
        self.name = name   

def restrictedTraverse(self, path, securityManager,  
                       get=getattr, has=hasattr, N=None, M=[],
                       TupleType=type(()) ):

    REQUEST = {'path': path}     
    REQUEST['TraversalRequestNameStack'] = path = path[:] # Copy!
    if not path[0]:
        # If the path starts with an empty string, go to the root first.
        self = self.getPhysicalRoot()
        path.pop(0) 

    path.reverse()
    object = self
    done = []
    while path:
        name = path.pop()
        __traceback_info__ = TraversalError(done, name)

        # Try an attribute.
        o = get(object, name, M)
        if o is M:
            # Try an item.
            try:
                # XXX maybe in Python 2.2 we can just check whether
                # the object has the attribute "__getitem__"
                # instead of blindly catching exceptions.
                o = object[name]
            except AttributeError, exc:
                if str(exc).find('__getitem__') >= 0:
                    # The object does not support the item interface.
                    # Try to re-raise the original attribute error.
                    # XXX I think this only happens with
                    # ExtensionClass instances.
                    get(object, name)
                raise
            except TypeError, exc:
                if str(exc).find('unsubscriptable') >= 0:
                    # The object does not support the item interface.
                    # Try to re-raise the original attribute error.
                    # XXX This is sooooo ugly.
                    get(object, name)
                raise

        object = o
        done.append((name, o))

    return object

