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
__doc__='''Tree manipulation classes

$Id: Tree.py,v 1.1 2003/03/01 20:25:14 kesmit Exp $'''
__version__='$Revision: 1.1 $'[11:-2]

from types import ListType, TupleType

class TreeNode:
    __allow_access_to_unprotected_subobjects__ = 1
    state = 0 # leaf
    height = 1
    size = 1
    def __init__(self):
        self._child_list = []
    def _add_child(self, child):
        'Add a child which already has all of its children.'
        self._child_list.append(child)
        self.height = max(self.height, child.height + 1)
        self.size = self.size + child.size
    def flat(self):
        'Return a flattened preorder list of tree nodes'
        items = []
        self.walk(items.append)
        return items
    def walk(self, f, data=None):
        'Preorder walk this tree, passing each node to a function'
        if data is None:
            f(self)
        else:
            f(self, data)
        for child in self._child_list:
            child.__of__(self).walk(f, data)
    def _depth(self):
        return self.aq_parent.depth + 1
    def __getitem__(self, index):
        return self._child_list[index].__of__(self)
    def __len__(self):
        return len(self._child_list)
    def __getattr__(self, name):
        if name == 'depth':
            return self._depth()
        raise AttributeError, name

_marker = []

class TreeMaker:
    '''Class for mapping a hierachy of objects into a tree of nodes.'''

    __allow_access_to_unprotected_subobjects__ = 1

    _id = 'tpId'
    _values = 'tpValues'
    _assume_children = 0
    _values_filter = None
    _values_function = None
    _state_function = None
    _expand_root = 1

    _cached_children = None

    def setChildAccess(self, attrname=_marker, filter=_marker,
                       function=_marker):
        '''Set the criteria for fetching child nodes.

        Child nodes can be accessed through either an attribute name
        or callback function.  Children fetched by attribute name can
        be filtered through a callback function.
        '''
        if function is _marker:
            self._values_function = None
            if attrname is not _marker:
                self._values = str(attrname)
            if filter is not _marker:
                self._values_filter = filter
        else:
            self._values_function = function

    def setIdAttr(self, id):
        """Set the attribute or method name called to get a unique Id.

        The id attribute or method is used to get a unique id for every node in
        the tree, so that the state of the tree can be encoded as a string using
        Tree.encodeExpansion(). The returned id should be unique and stable
        across Zope requests.

        If the attribute or method isn't found on an object, either the objects
        persistence Id or the result of id() on the object is used instead.

        """
        self._id = id

    def setExpandRoot(self, expand):
        """Set wether or not to expand the root node by default.
        
        When no expanded flag or mapping is passed to .tree(), assume the root
        node is expanded, and leave all subnodes closed.

        The default is to expand the root node.
        
        """
        self._expand_root = not not expand

    def setAssumeChildren(self, assume):
        """Set wether or not to assume nodes have children.
        
        When a node is not expanded, when assume children is set, don't
        determine if it is a leaf node, but assume it can be opened. Use this
        when determining the children for a node is expensive.
        
        The default is to not assume there are children.
        
        """
        self._assume_children = not not assume

    def setStateFunction(self, function):
        """Set the expansion state function.

        This function will be called to determine if a node should be open or
        collapsed, or should be treated as a leaf node. The function is passed
        the current object, and the intended state for that object. It should
        return the actual state the object should be in. State is encoded as an
        integer, meaning:

            -1: Node closed. Children will not be processed.
             0: Leaf node, cannot be opened or closed, no children are
                processed.
             1: Node opened. Children will be processed as part of the tree.
        
        """
        self._state_function = function

    def tree(self, root, expanded=None, subtree=0):
        '''Create a tree from root, with specified nodes expanded.

        "expanded" must be false, true, or a mapping.
        Each key of the mapping is the id of a top-level expanded
        node, and each value is the "expanded" value for the
        children of that node.
        '''
        node = self.node(root)
        child_exp = expanded
        if not simple_type(expanded):
            # Assume a mapping
            expanded = expanded.has_key(node.id)
            child_exp = child_exp.get(node.id)

        expanded = expanded or (not subtree and self._expand_root)
        # Set state to 0 (leaf), 1 (opened), or -1 (closed)
        state = self.hasChildren(root) and (expanded or -1)
        if self._state_function is not None:
            state = self._state_function(node.object, state)
        node.state = state
        if state > 0:
            for child in self.getChildren(root):
                node._add_child(self.tree(child, child_exp, 1))

        if not subtree:
            node.depth = 0
        return node

    def node(self, object):
        node = TreeNode()
        node.object = object
        node.id = b2a(self.getId(object))
        return node

    def getId(self, object):
        id_attr = self._id
        if hasattr(object, id_attr):
            obid = getattr(object, id_attr)
            if not simple_type(obid): obid = obid()
            return obid
        if hasattr(object, '_p_oid'): return str(object._p_oid)
        return id(object)

    def hasChildren(self, object):
        if self._assume_children:
            return 1
        # Cache generated children for a subsequent call to getChildren
        self._cached_children = (object, self.getChildren(object))
        return not not self._cached_children[1]

    def getChildren(self, object):
        # Check and clear cache first
        if self._cached_children is not None:
            ob, children = self._cached_children
            self._cached_children = None
            if ob is object:
                return children
    
        if self._values_function is not None:
            return self._values_function(object)

        children = getattr(object, self._values)
        if not (isinstance(children, ListType) or
                isinstance(children, TupleType)):
            # Assume callable; result not useful anyway otherwise.
            children = children()

        return self.filterChildren(children)

    def filterChildren(self, children):
        if self._values_filter:
            return self._values_filter(children)
        return children

def simple_type(ob,
                is_simple={type(''):1, type(0):1, type(0.0):1,
                           type(0L):1, type(None):1 }.has_key):
    return is_simple(type(ob))

from binascii import b2a_base64, a2b_base64
from string import translate, maketrans
import zlib

a2u_map = maketrans('+/=', '-._')
u2a_map = maketrans('-._', '+/=')

def b2a(s):
    '''Encode a value as a cookie- and url-safe string.

    Encoded string use only alpahnumeric characters, and "._-".
    '''
    s = str(s)
    if len(s) <= 57:
        return translate(b2a_base64(s)[:-1], a2u_map)
    frags = []
    for i in range(0, len(s), 57):
        frags.append(b2a_base64(s[i:i + 57])[:-1])
    return translate(''.join(frags), a2u_map)

def a2b(s):
    '''Decode a b2a-encoded string.'''
    s = translate(s, u2a_map)
    if len(s) <= 76:
        return a2b_base64(s)
    frags = []
    for i in range(0, len(s), 76):
        frags.append(a2b_base64(s[i:i + 76]))
    return ''.join(frags)

def encodeExpansion(nodes, compress=1):
    '''Encode the expanded node ids of a tree into a string.

    Accepts a list of nodes, such as that produced by root.flat().
    Marks each expanded node with an expansion_number attribute.
    Since node ids are encoded, the resulting string is safe for
    use in cookies and URLs.
    '''
    steps = []
    last_depth = -1
    n = 0
    for node in nodes:
        if node.state <=0: continue
        dd = last_depth - node.depth + 1
        last_depth = node.depth
        if dd > 0:
            steps.append('_' * dd)
        steps.append(node.id)
        node.expansion_number = n
        n = n + 1
    result = ':'.join(steps)
    if compress:
        result = ':'  + b2a(zlib.compress(result, 9))
    return result

def decodeExpansion(s, nth=None):
    '''Decode an expanded node map from a string.

    If nth is an integer, also return the (map, key) pair for the nth entry.
    '''
    if len(s) > 8192: # Set limit to 8K, to avoid DoS attacks.
        raise ValueError('Encoded node map too large')

    if s[0] == ':': # Compressed state
        s = zlib.decompress(a2b(s[1:]))
    
    map = m = {}
    mstack = []
    pop = 0
    nth_pair = None
    if nth is not None:
        nth_pair = (None, None)
    for step in s.split(':'):
        if step[0] == '_':
            pop = len(step) - 1
            continue
        if pop < 0:
            mstack.append(m)
            m[obid] = {}
            m = m[obid]
        elif map:
            m[obid] = None
        if len(step) == 0:
            return map
        obid = step
        if pop > 0:
            m = mstack[-pop]
            del mstack[-pop:]
        pop = -1
        if nth == 0:
            nth_pair = (m, obid)
            nth = None
        elif nth is not None:
            nth = nth - 1
    m[obid] = None
    if nth == 0:
        return map, (m, obid)
    if nth_pair is not None:
        return map, nth_pair
    return map
