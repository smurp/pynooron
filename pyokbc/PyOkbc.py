__version__='$Revision: 1.22 $'[11:-2]
__cvs_id__ ='$Id: PyOkbc.py,v 1.22 2002/12/04 18:08:12 smurp Exp $'

PRIMORDIAL_KB = ()
OKBC_SPEC_BASE_URL =  "http://www.ai.sri.com/~okbc/spec/okbc2/okbc2.html#"


import string
import sys
import copy
import os

from  OkbcConditions import *
from Constraints import Constrainable

##########################################
#    Debugging utils
##########################################

DEBUG_METHODS =[]# ['get_slot_values_in_detail_recurse']
DEBUG = 0
WARNINGS = 2
TRACE_HTML = 0
# 10 critical
# 20 noops
# 30 subtleties


def trayce(args=[],format=None,indent=None):
    meth = None
    (ppre,pre,inter,post,ppost) = TRACE_HTML and \
                       ("<table>","<tr><td>","<td>","</tr>","</table>") or \
                       ("",""," ","","")
    if format:
        mess = format % args
    else:
        mess = string.join(map(str,args),inter)
    try:
        raise
    except:
        (typ,val,tb) = sys.exc_info()
        #stack = traceback.extract_stack(tb)
        code = tb.tb_frame.f_back.f_code        
        meth = code.co_name
    if DEBUG:
        if meth in DEBUG_METHODS:
            if indent == None:
                print pre,meth,inter,mess,post
            else:
                print pre,indent,mess,post
            if 0:
                for m in ['co_filename','co_nlocals',
                          'co_varnames','co_consts',
                          'co_cellvars','co_name','co_firstlineno']:
                    print "  ",m,":",eval("code.%s"%m)
            if 0:                    
                for m in dir(code):
                    print "  ",m,":",eval("code.%s"%m)
                
def warn(mess,level=10):
    if WARNINGS >= level:
        print mess

def uniquify_specs(list_of_specs):
    seen_vals = []
    indx = 0
    while indx < len(list_of_specs):
        spec = list_of_specs[indx]
        if spec[0] in seen_vals:
            list_of_specs.pop(indx)
        else:
            seen_vals.append(spec[0])
            indx = indx + 1
    #print "SEENVALS",seen_vals
    #print "UNIQUE! ",list_of_specs


##########################################
#    Classes
##########################################    
# 
# Oh, order is *so* important below!  Bootstrapping madness!
# If you have any idea how to do a better job of this, please
# tell smurp@emergence.com
#

class Symbol:
    __allow_access_to_unprotected_subobjects__ = 1 # for ZPT security    
    def __init__(self,name):
        self._name = name
    def __str__(self):
        try:
            return self._name
        except:
            return 'unknown'
    def __repr__(self):
        return str(self)
        return "<"+str(self)+">"
    def __doc__(self):
        return "http://www.ai.sri.com/~okbc/spec/okbc2/okbc2.html#"+self.name

class Node(Symbol):
    pass

class FRAME(Node):
    __allow_access_to_unprotected_subobjects__ = 1
        
    def __init__(self,frame_name,kb=None,frame_type=None):
        self._name = frame_name
        #self._frame_type = frame_type
        #if not frame_type :
        #    warn('FRAME.__init__ has no frame_type for '+frame_name)
        self._kb = kb
        self._direct_types = []
        self._frame_in_cache_p = 0
        self._pretty_name = None
        if kb:
            kb._add_frame_to_cache(self)
        self._own_slots = {}
        self._template_slots = {}
        self._doc = None
        self._direct_superclasses = []        

    def __str__(self):
        #return "<"+self._name+">"
        return self._name

    #def __repr__(self):
    #    return str(self)


class KLASS(FRAME): pass

class INDIVIDUAL(FRAME): pass
        
class SLOT(FRAME): pass

class FACET(FRAME): pass

Node._class = KLASS(':class')
Node._class._frame_type = Node._class
KLASS._frame_type = Node._class

Node._facet = FACET(':facet')
Node._facet._frame_type = Node._class
FACET._frame_type = Node._facet

Node._slot = SLOT(':slot')
Node._slot._frame_type = Node._class
SLOT._frame_type = Node._slot

Node._individual = INDIVIDUAL(':individual')
Node._individual._frame_type = Node._class
INDIVIDUAL._frame_type = Node._individual


primordials = []
def primordialFACET(name):
    o = FACET(name,)
    primordials.append(o)
    return o
def primordialSLOT(name):
    o = SLOT(name)
    primordials.append(o)
    return o
def primordialKLASS(name):
    o = KLASS(name)
    primordials.append(o)
    return o
def primordialINDIVIDUAL(name):
    o = INDIVIDUAL(name)
    primordials.append(o)
    return o

primordial = {}

primordial['kwarg'] = (':all',':own',':template',':taxonomic',
                       ':direct',':default-only',':known-true',
                       ':either',':more',':value',':frame',
                       ':system-default',':frames',':default',
                       ':filled',':port',':host',':password',
                       ':username',':parent-kbs')
# standard facets
primordial['facet'] = (":VALUE-TYPE",":INVERSE",":CARDINALITY",
                       ":VALUE-TYPE",":MAXIMUM-CARDINALITY",
                       ":MINIMUM-CARDINALITY",":SAME-VALUES",
                       ":NOT-SAME-VALUES",":SUBSET-OF-VALUES",
                       ":NUMERIC-MINIMUM",":NUMERIC-MAXIMUM",
                       ":SAME-VALUES", ":SOME-VALUES",
                       ":COLLECTION-TYPE",
                       ":DOCUMENTATION-IN-FRAME")

# Slots on slot frames okbc2.html#3169
primordial['slot'] = (":DOCUMENTATION",
                      ":DOMAIN",":SLOT-VALUE-TYPE",":SLOT-INVERSE",
                      ":SLOT-CARDINALITY",":SLOT-MAXIMUM-CARDINALITY",
                      ":SLOT-MINIMUM-CARDINALITY",":SLOT-SAME-VALUES",
                      ":SLOT-NOT-SAME-VALUES",":SLOT-SUBSET-OF-VALUES",
                      ":SLOT-NUMERIC-MINIMUM",":SLOT-NUMERIC-MAXIMUM",
                      ":SLOT-SOME-VALUES",":SLOT-COLLECTION-TYPE")

primordial['class'] = (":INDIVIDUAL",
                       ":SLOT",":FACET",":KB",
                       ":NUMBER",":INTEGER",":STRING",
                       ":SEXPR",":SYMBOL",":LIST")

primordial['individual'] = ()

primordial['behavior_value'] = (':never',':immediate',
                                ':user-defined-facets', ':facets-reported',
                                ':read-only',':monotonic',
                                ':deferred',':background',':override',
                                ':when-consistent',':none',':list',
                                ':bag',':set')
primordial['behavior_type'] = (':are-frames',':class-slot-types',
                               ':collection-types',':compliance',
                               ':constraints-checked',
                               ':constraint-checking-time',
                               ':constraint-report-time',
                               ':defaults')

Node._THING = primordialKLASS(":THING")
Node._CLASS = primordialKLASS(":CLASS")

Node.kwargs = {}

def bootstrap(primordial = primordial):
    types_in_order = ['kwarg','facet','slot','class','individual',
                      'behavior_type','behaviour_value']
    types = (('kwarg',          Symbol),
             ('class',          primordialKLASS),             
             ('facet',          primordialFACET),
             ('slot',           primordialSLOT),
             ('individual',     primordialINDIVIDUAL),
             ('behavior_type',  Symbol),
             ('behavior_value', Symbol),
             )
    for typ,construct in types:
        for name in primordial[typ]:
            pyname = name
            pyname = pyname.replace("-","_")
            pyname = pyname.replace(":","_")
            #print pyname,name
            thang = construct(name)
            Node.__dict__[pyname] = thang
            if typ == 'kwarg':
                public_name = pyname[0] == '_' and pyname[1:] or pyname
                Node.kwargs[public_name.upper()] = thang
            if typ == 'class':
                #print "doing it to",pyname
                Node.__dict__[pyname]._direct_types = [Node._CLASS]
                Node.__dict__[pyname]._direct_superclasses = [Node._THING]
            if typ == 'facet':
                thang._direct_types.append(Node._FACET)
            if typ == 'slot':
                thang._direct_types.append(Node._SLOT)

bootstrap()


# see CLASS_RECURSION comments
Node._THING._direct_types = [Node._CLASS]
Node._CLASS._direct_superclasses = [Node._THING]

Node._FACET.  _direct_superclasses.append(Node._INDIVIDUAL)
Node._SLOT .  _direct_superclasses.append(Node._INDIVIDUAL)
Node._NUMBER. _direct_superclasses.append(Node._INDIVIDUAL)
Node._INTEGER._direct_superclasses.append(Node._NUMBER)
Node._STRING. _direct_superclasses.append(Node._INDIVIDUAL)
Node._SYMBOL. _direct_superclasses.append(Node._SEXPR)
Node._LIST.   _direct_superclasses.append(Node._INDIVIDUAL)

def class_dump(which):
    for w in which:
        print w,"_direct_types",w._direct_types
#class_dump([Node._THING,Node._CLASS,Node._STRING])

Node._behaviors = { # not in OKBC spec, but implied
    Node._are_frames:               (Node._class,
                                     Node._individual,
                                     Node._slot,
                                     Node._facet),
    Node._class_slot_types:         (Node._template,
                                     Node._own),
    Node._collection_types:         (Node._list,
                                     Node._set,
                                     Node._bag,
                                     Node._none),
    Node._compliance:               (Node._facets_reported,
                                     Node._user_defined_facets,
                                     Node._read_only,
                                     Node._monotonic),
    Node._constraints_checked:      (Node._VALUE_TYPE,
                                     Node._INVERSE,
                                     Node._CARDINALITY,
                                     Node._MAXIMUM_CARDINALITY,
                                     Node._MINIMUM_CARDINALITY,
                                     Node._SAME_VALUES,
                                     Node._NOT_SAME_VALUES,
                                     Node._SUBSET_OF_VALUES,
                                     Node._NUMERIC_MINIMUM,
                                     Node._NUMERIC_MAXIMUM,
                                     Node._SOME_VALUES,
                                     Node._COLLECTION_TYPE,
                                     Node._DOCUMENTATION_IN_FRAME),
    Node._constraint_checking_time: (Node._immediate,
                                     Node._deferred,
                                     Node._background,
                                     Node._never),
    Node._constraint_report_time:   (Node._immediate,
                                     Node._deferred),
    Node._defaults:                 (Node._override,
                                     Node._when_consistent,
                                     Node._none)}

# see constraints.lisp
Node._equivalent_constraint_facets = {
    Node._SLOT_INVERSE:             Node._INVERSE,
    Node._SLOT_VALUE_TYPE :         Node._VALUE_TYPE,
    Node._SLOT_CARDINALITY:         Node._CARDINALITY,
    Node._SLOT_MAXIMUM_CARDINALITY: Node._MAXIMUM_CARDINALITY,
    Node._SLOT_MINIMUM_CARDINALITY: Node._MINIMUM_CARDINALITY,
    Node._SLOT_SAME_VALUES:         Node._SAME_VALUES,
    Node._SLOT_NOT_SAME_VALUES:     Node._NOT_SAME_VALUES,
    Node._SLOT_SUBSET_OF_VALUES:    Node._SUBSET_OF_VALUES,
    Node._SLOT_NUMERIC_MINIMUM:     Node._NUMERIC_MINIMUM,
    Node._SLOT_NUMERIC_MAXIMUM:     Node._NUMERIC_MAXIMUM,
    Node._SLOT_SOME_VALUES:         Node._SOME_VALUES,
    Node._SLOT_COLLECTION_TYPE:     Node._COLLECTION_TYPE }

# not in OKBC spec
Node._selector_all             = (Node._all,Node._frames,Node._system_default)
Node._target_contexts          = (Node._frame,Node._slot,Node._facet,Node._class,Node._individual,Node._value)
Node._frame_types              = (Node._class,Node._individual,Node._slot,Node._facet)
Node._number_of_values         = (Node._all,Node._more)
Node._value_selectors          = (Node._either,Node._default_only,Node._known_true)
Node._slot_types               = (Node._all,Node._template,Node._own)
Node._inference_levels         = (Node._taxonomic,Node._all,Node._direct)

class Programmable:
    def call_procedure(kb,procedure,arguments=None):
        return apply(procedure,arguments)
    
    def create_procedure(kb,arguments=None,body=None,environment=None):
        # For the moment, body must be a python function, for example
        #   def boo():
        #       return "boo"
        #   create_procedure(body=boo)
        # This is obviously abominable, first because it doesn't obey the
        # spec, but also because it has nasty security implications.
        # Regardless, I will implement this shortcut so call_procedure
        # can immediately be used for such simple things as sorting.
        # Likewise, environment and arguments are simply dropped.
        # The goal of this implementation is to make it possible to use
        # call_procedure AS IF procedures were properly implemented.  This
        # works nicely with the inanity of PyKb files simply being python.
        # See /know/convenience_procedures.pykb for examples.
        return body
    
    def get_procedure(kb,name):
        for kaybee in [kb] +  kb.get_kb_parents():
            if not hasattr(kaybee,'_procedures'):
                kaybee._procedures={}
            proc = kaybee._procedures.get(name)
            if proc: return proc
        return None
    
    def register_procedure(kb,name,procedure):
        if not hasattr(kb,'_procedures'):
            kb._procedures={}
        kb._procedures[name]=procedure

    def unregister_procedure(kb,name):
        if not hasattr(kb,'_procedures'):
            kb._procedures={}
        del kb._procedures[name]

class KB(FRAME,Programmable):
    """All OKBC methods which take a KB argument should be implemented here.
    The exceptions are the mandatory ones.  All of them are implemented in
    TupleKB.  That leaves all optional methods, which should be implemented
    here.  Oh I am sure this is all screwed up!"""
    __allow_access_to_unprotected_subobjects__ = 1
    def __init__(self,name,initargs = {},connection=None):
        if connection:
            kb = connection.meta_kb()
        else:
            kb = None
        self._connection = connection
        node_kb = Node.__dict__.get('_kb') # equivalent to Node._kb see below
        FRAME.__init__(self,name,frame_type=node_kb,kb=kb)
        self._direct_types.append(Node._KB)
        self._initargs = initargs
        
        parent_kbs = initargs.get(Node._parent_kbs,[])
        if PRIMORDIAL_KB: parent_kbs.append(PRIMORDIAL_KB) #FIXME not always!
        self._parent_kbs = parent_kbs 
    
    def kb_p(kb):
        return 1

    def class_p(kb,thing,kb_local_only_p = 0):
        return isinstance(thing,KLASS)

    def coerce_to_class(kb,thing,error_p = 1,kb_local_only_p = 0):
        klop = kb_local_only_p
        if kb.class_p(thing):
            return (thing,1)
        (found_class,class_found_p) = kb.get_frame_in_kb(thing,
                                                         kb_local_only_p=klop)
        if found_class:
            return (found_class,class_found_p)
        #warn(str( thing)+" being coerced to class in "+str(kb))
        found_class = kb.create_frame_internal(thing,Node._class)
        class_found_p = found_class
        if not class_found_p and error_p:
            raise ClassNotFound,(thing,kb)
        return (found_class,class_found_p)

    def connection(kb):# FIXME not part of OKBC Spec
        return kb._connection
    
    def create_frame_internal(kb,name,frame_type,
                              direct_types=[],
                              direct_superclasses=[],
                              doc = None,
                              template_slots=[],
                              template_facets=[],
                              own_slots=[],
                              own_facets=[],
                              primitive_p=1,
                              handle=None,
                              pretty_name=None,
                              kb_local_only_p=0):
        #print name,"being inserted into", kb
        if kb != current_kb():
            print "noncurrent kb",kb,"for",name
        klop = kb_local_only_p
        is_name = type(name) == type('')
        if is_name:
            if frame_type == Node._class:
                frame = KLASS(name,kb,frame_type=frame_type)
            elif frame_type == Node._individual:
                frame = INDIVIDUAL(name,kb,frame_type=frame_type)
            elif frame_type == Node._slot:
                frame = SLOT(name,kb,frame_type=frame_type)
            elif frame_type == Node._facet:
                frame = FACET(name,kb,frame_type=frame_type)
            else:
                raise GenericError()
        elif not isinstance(name,FRAME):
            # name is neither a string nor an existing FRAME
            # We permit FRAMEs because of possible circularities when
            # a kb is being read in.
            raise GenericError()

        if frame_type == Node._slot:
            if not (Node._SLOT in direct_types) and \
               not (':SLOT' in direct_types):
                direct_types.append(Node._SLOT)
            
        if frame_type == Node._facet:
            if not (Node._facet in direct_types) and \
               not (':FACET' in direct_types):
                direct_types.append(Node._FACET)

        if frame_type == Node._class:
            if not (Node._CLASS in direct_types) and \
               not (':CLASS' in direct_types):
                direct_types.append(Node._CLASS)
            if not (Node._THING in direct_superclasses) and \
               not (':THING' in direct_superclasses):
                direct_superclasses.append(Node._THING)
            kb.put_class_superclasses(frame,direct_superclasses,
                                      kb_local_only_p = klop)
        else:
            if not (Node._INDIVIDUAL in direct_types) and \
               not (':INDIVIDUAL' in direct_types):
                direct_types.append(Node._INDIVIDUAL)

        kb.put_instance_types(frame,direct_types,
                              kb_local_only_p = kb_local_only_p)

        for slot_spec in own_slots:
            slot = slot_spec[0]
            slot_values = []            
            for slot_value_spec in slot_spec[1:]:
                if (type(slot_value_spec) in [type([]),type(())]):
                    if slot_value_spec[0] == Node._default:
                        pass #save a default value slot_value_spec[1]
                    else:
                        pass # we are in a list but first elem != default
                else:
                    slot_values.append(slot_value_spec)
            kb.put_slot_values(frame,slot,slot_values,
                               kb_local_only_p=kb_local_only_p)

        for slot_spec in template_slots:
            slot = slot_spec[0]
            slot_values = []            
            for slot_value_spec in slot_spec[1:]:
                if (type(slot_value_spec) in [type([]),type(())]):
                    if slot_value_spec[0] == Node._default:
                        pass #save a default value slot_value_spec[1]
                    else:
                        pass # we are in a list but first elem != default
                else:
                    slot_values.append(slot_value_spec)
            kb.put_slot_values(frame,slot,slot_values,
                               slot_type=Node._template,
                               kb_local_only_p=kb_local_only_p)

        if doc: frame._doc = doc
        if doc:
            kb.put_slot_value(frame,Node._DOCUMENTATION,
                              doc,slot_type=Node._own,
                              kb_local_only_p=1)
            #print kb
            #print "and it is there:",kb.get_slot_value(frame,Node._DOCUMENTATION)
        if pretty_name != None: frame._pretty_name = pretty_name
        

        
        return frame
    create_frame = create_frame_internal

    def create_slot_internal(kb, name, 
                             frame_or_nil = None,
                             slot_type = Node._all,
                             direct_types = [],
                             doc = None,
                             own_slots = [],
                             own_facets = [],
                             handle = None,
                             pretty_name = None,
                             kb_local_only_p = 0):
        slot = kb.create_frame_internal(name,
                                        frame_type = Node._slot,
                                        direct_types = direct_types,
                                        doc = doc,
                                        own_slots = own_slots,
                                        own_facets = own_facets,
                                        handle = handle,
                                        pretty_name = pretty_name,
                                        kb_local_only_p = kb_local_only_p)
        
        return slot
    create_slot = create_slot_internal

    def facet_p(kb,thing,kb_local_only_p=0):
        return isinstance(thing,FACET)

    def frame_in_kb_p(kb,thing,kb_local_only_p=0):
        is_in = kb.frame_in_kb_p_internal(thing,kb_local_only_p)
        if not kb_local_only_p:
            for kaybee in kb.get_kb_parents():
                if kaybee.frame_in_kb_p(thing,kb_local_only_p=1):
                    is_in = 1
                    break
        return is_in

    def frame_p(kb,thing,kb_local_only_p = 0): # FIXME not in OKBC Spec
        return isinstance(thing,FRAME)


    _behavior_values = {Node._are_frames : [Node._class,
                                            Node._individual,
                                            Node._slot,
                                            Node._facet],
                        Node._class_slot_types : [Node._template],
                        Node._collection_types : [Node._list],
                        Node._constraint_checking_time : [Node._never],
                        Node._constraint_report_time : [Node._never],
                        Node._constraints_checked : [],
                        Node._defaults : [Node._override]}

    def get_behavior_values_internal(kb,behavior):
        return kb._behavior_values.get(behavior,[])
    get_behavior_values = get_behavior_values_internal

    def get_class_instances_internal(kb,klass,
                                     inference_level=Node._taxonomic,
                                     number_of_values=Node._all,
                                     kb_local_only_p=1):
        (list_of_instances,exact_p,more_status) = ([],1,0)
        for frame in kb.get_kb_frames():
            if kb.instance_of_p(frame,klass,
                                inference_level,
                                kb_local_only_p)[0]:
                list_of_instances.append(frame)
        return (list_of_instances,exact_p,more_status)

    def get_class_instances(kb,klass,
                            inference_level=Node._taxonomic,
                            number_of_values=Node._all,
                            kb_local_only_p=0):
        return kb.get_class_instances_recurse(klass,
                                              inference_level,
                                              number_of_values,
                                              kb_local_only_p,[])
    
    def get_class_instances_recurse(kb,klass,
                                    inference_level=Node._taxonomic,
                                    number_of_values=Node._all,
                                    kb_local_only_p=1,
                                    checked_kbs=[]):
        (klass,class_found_p) = kb.coerce_to_class(klass)
        checked_kbs.append(kb)
        rets = kb.get_class_instances_internal(klass,
                                               inference_level,
                                               number_of_values,
                                               kb_local_only_p=1)
        (list_of_instances,exact_p,more_status) = rets
        if not kb_local_only_p:
            for parent in kb.get_kb_direct_parents():
                if not (parent in checked_kbs):
                    checked_kbs.append(parent)
                    rets = parent.get_class_instances_recurse(klass,
                                                              inference_level,
                                                              number_of_values,
                                                              kb_local_only_p,
                                                              checked_kbs)
                    for inst in rets[0]:
                        if not inst in list_of_instances:
                            list_of_instances.append(inst)
        return (list_of_instances,exact_p,more_status)

    def get_class_subclasses(kb,klass,
                             inference_level = Node._taxonomic,
                             number_of_values = Node._all,
                             kb_local_only_p = 0):
        (klass,class_found_p) = kb.coerce_to_class(klass)
        #checked_kbs.append(kb)
        if inference_level != Node._direct:
            warn('get_class_subclasses ignores inference_level > direct')
        (subs,
         exact_p,
         more_status) = kb.get_class_subclasses_internal(klass,
                                                inference_level,
                                                number_of_values,
                                                kb_local_only_p=1)
        if not kb_local_only_p:
            for parent in kb.get_kb_parents():
                rets = parent.get_class_subclasses(klass,
                                                   inference_level,
                                                   number_of_values,
                                                   kb_local_only_p)[0]
                for sub in rets:
                    if not (sub in subs):
                        subs.append(sub)
        return (subs,exact_p,more_status)

##    def get_class_superclasses(kb,klass,
##                               inference_level = Node._taxonomic,
##                               number_of_values = Node._all,
##                               kb_local_only_p = 0):
##        superclasses=[]
##        return kb.get_class_superclasses_extend(klass,
##                                                inference_level,
##                                                number_of_values,
##                                                kb_local_only_p,
##                                                superclasses)
    
    def get_class_superclasses(kb,klass,
                               inference_level = Node._taxonomic,
                               number_of_values = Node._all,
                               kb_local_only_p = 0,
                               superclasses = []):
        if Node._INDIVIDUAL in superclasses:
            print klass, "sub of INDIVIDUAL",superclasses,"doh"
            #raise "youch","woof"
        (klass,class_found_p) = kb.coerce_to_class(klass)
        (supers,exact_p,more_status) =\
               kb.get_class_superclasses_internal(klass,
                                                  inference_level,
                                                  number_of_values,
                                                  kb_local_only_p)
        warn('get_class_superclasses is not properly recursive')
        return (supers,exact_p,more_status)

        for super in supers:
            if not (super in superclasses):
                #if Node._INDIVIDUAL == super: print klass, "sub of INDIVIDUAL",superclasses
                superclasses.append(super)
                more_supers = kb.get_class_superclasses(super,
                                                        inference_level,
                                                        number_of_values,
                                                        kb_local_only_p)[0]
                #print "more_supers",super,more_supers
                for more_super in more_supers:
                    if not (more_super in superclasses):
                        superclasses.append(more_super)
        #if Node._INDIVIDUAL in superclasses: print klass, "sub of INDIVIDUAL",superclasses
        return (superclasses,exact_p,more_status)

    def get_frame_in_kb(kb,thing,error_p=1,kb_local_only_p=0,
                        checked_kbs=None): # FIXME shouldn't add arg!
        (found_frame,
         frame_found_p)\
         = kb.get_frame_in_kb_internal(thing,error_p,kb_local_only_p)
        if frame_found_p or kb_local_only_p:
            return (found_frame,frame_found_p)
        if checked_kbs == None:
            checked_kbs = []
        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                rets = parent.get_frame_in_kb(thing,error_p,kb_local_only_p,
                                              checked_kbs)
                if rets[1]: return rets
        return (None,None)
        
    def get_frame_name_internal(kb,frame,kb_local_only_p=0):
        # FIXME get_frame_name_internal needs fixing
        #frame = kb.get_frame_in_kb(frame)[0]
        if frame != None:
            return str(frame)
            return frame._name
        return None
    get_frame_name = get_frame_name_internal

    def get_frame_pretty_name(kb,frame,kb_local_only_p=0):
        pretty_name = kb.get_frame_pretty_name_internal(frame,
                                                        kb_local_only_p)
        if pretty_name != None:
            return pretty_name
        if not kb_local_only_p:
            for kaybee in kb.get_kb_parents():
                kaybee_pn = kaybee.get_frame_pretty_name(frame,
                                                         kb_local_only_p=1)
                if kaybee_pn != None:
                    return kaybee_pn
        return pretty_name

    def get_frame_sentences(kb, frame,
                            number_of_values=Node._all,
                            okbc_sentences_p=1,value_selector=Node._either,
                            kb_local_only_p=0):
        exact_p = 1
        more_status = 0
        orig_frame = frame
        (frame,frame_found_p) = kb.get_frame_in_kb(frame)
        if not frame_found_p:
            #raise IndividualNotFound(orig_frame,kb)
            return ([],0,0)

        frame_name = kb.get_frame_name(frame)
        frame_type = kb.get_frame_type(frame)
        frame_type_string = str(frame_type)[1:]

        lines = []
        def tel(st,lines=lines):
            if type(st) == type(""):
                lines.append("(" + st +")")
            elif type(st) == type([]):
                st = map(lambda x: str(x),st)
                lines.append("(" + string.join(st," ") + ")")
                
        tel(frame_type_string + " " + frame_name )

        for klass in kb.get_instance_types(frame,
                                           inference_level=Node._direct)[0]:
            tel(["instance-of",frame_name,klass])

        if kb.class_p(frame):
            get_supers = kb.get_class_superclasses
            for klass in get_supers(frame,
                                    inference_level=Node._direct)[0]:
                tel(["subclass-of",frame_name,klass])                

        for slot in kb.get_frame_slots(frame,slot_type=Node._own)[0]:
            some = 0
            for val in kb.get_slot_values(frame,slot,slot_type=Node._own)[0]:
                some = 1
                if type(val) == type(''):
                    val = '"' + val + '"'
                tel(["slot",slot,frame_name,val])
            if not some:
                tel(["slot-of",slot,frame_name])

        for slot in kb.get_frame_slots(frame,slot_type=Node._template,
                                       inference_level=Node._direct)[0]:
            some = 0
            #print "slot =",slot,slot.__class__,slot.__class__.__bases__
            for val in kb.get_slot_values(frame,slot,Node._template)[0]:
                some = 1
                tel(["template-slot-value",slot,frame,val])
            if not some:
                tel(['template-slot-of',slot,frame_name])

        warn("get-frame-sentences skips prettyname, facets")
        pretty_name = kb.get_frame_pretty_name(frame)

        return (lines,exact_p,more_status)

    def get_frame_slots(kb,frame,
                        inference_level = Node._taxonomic,
                        slot_type = Node._all,
                        kb_local_only_p = 0):
        checked_kbs = []
        checked_classes = []
        return kb.get_frame_slots_recurse(frame,
                                          inference_level,
                                          slot_type,
                                          kb_local_only_p,
                                          checked_kbs,
                                          checked_classes)
                               
    def get_frame_slots_recurse(kb,frame,
                                inference_level = Node._taxonomic,
                                slot_type = Node._all,
                                kb_local_only_p = 0,
                                checked_kbs = [],
                                checked_classes = []):
        #print "get_frame_slots_recurse(",frame,kb,")"        
        klop = kb_local_only_p
        il = inference_level
        frame_orig = frame
        (frame,frame_found_p) = kb.get_frame_in_kb(frame)
        if not frame_found_p:
            #print frame_orig,"not found"
            return ([],1)
        (list_of_slots,
         exact_p) = kb.get_frame_slots_internal(frame,inference_level,
                                                slot_type,klop)
        #list_of_slot_names = map(lambda a:str(a),list_of_slots)
        #print "  primordial",list_of_slots,list_of_slot_names
        if not kb_local_only_p:
            for kaybee in kb.get_kb_direct_parents():
                if kaybee in checked_kbs:
                    continue
                slots = kaybee.get_frame_slots_recurse(frame,inference_level,
                                                      slot_type,
                                                      kb_local_only_p,
                                                      checked_kbs,
                                                      checked_classes)[0]
                for s in slots:
                    #if not (s in list_of_slots or str(s) in list_of_slot_names):
                    if not (s in list_of_slots):
                        #if str(s) == "'npt_for_self'": print "  assigning",list_of_slots,list_of_slot_names
                        #list_of_slot_names.append(str(s))
                        list_of_slots.append(s)
                    #if not (s in list_of_slots):
                    #    list_of_slots.append(s)
                checked_kbs.append(kaybee)
                
        #if DEBUG: print "get_frame_slots",kb,frame
        if inference_level in [Node._all,Node._taxonomic] and \
           slot_type in [Node._template,Node._all]:
            typs = kb.get_instance_types(frame, inference_level = Node._all,
                                         number_of_values = Node._all,
                                         kb_local_only_p = klop)[0]
            for klass in typs:
                #if DEBUG: print "  klass:",klass
                if klass in checked_classes:
                    continue
                checked_classes.append(klass)
                if klass == frame:
                    continue
                if kb_local_only_p \
                   and not kb.frame_in_kb_p(klass,kb_local_only_p=1):
                    continue
                for s in  kb.get_frame_slots_recurse(klass,
                                                        inference_level,
                                                        Node._template,#slot_type
                                                        kb_local_only_p,
                                                        checked_kbs,
                                                        checked_classes)[0]:

                    #if not (s in list_of_slots or str(s) in list_of_slot_names):
                    if not (s in list_of_slots):
                        #if str(s) == "'npt_for_self'": print "  kb assigning",list_of_slots,list_of_slot_names
                        #list_of_slot_names.append(str(s))
                        list_of_slots.append(s)
        #print "  returning",list_of_slots
        return (list_of_slots,exact_p)

    def get_frame_type_internal(kb,thing,kb_local_only_p=0):
        return thing.get_frame_type()
    get_frame_type = get_frame_type_internal

    def CACHING_get_instance_types(kb,frame,
                           inference_level = Node._taxonomic,
                           number_of_values = Node._all,
                           kb_local_only_p = 0):
        """This method was about 10 percent slower than non-caching for
        profiling.py and caused 2 error in pyokbc/tests."""
        frame_name = str(frame)
        cache_key = frame_name + \
                    str(inference_level) + \
                    str(number_of_values) + \
                    str(kb_local_only_p)
        if not hasattr(kb,'_cached_get_instance_types'):
            kb._cached_get_instance_types = {}
        cached_types = kb._cached_get_instance_types.get(cache_key)
        if cached_types == None:
            checked_kbs = []
            cached_types = \
               kb.get_instance_types_recurse(frame,inference_level,
                                             number_of_values,
                                             kb_local_only_p,
                                             checked_kbs)
            kb._cached_get_instance_types[cache_key] = cached_types
        return cached_types

    def get_instance_types(kb,frame,
                           inference_level = Node._taxonomic,
                           number_of_values = Node._all,
                           kb_local_only_p = 0):
        checked_kbs = []
        return kb.get_instance_types_recurse(frame,inference_level,
                                             number_of_values,
                                             kb_local_only_p,
                                             checked_kbs)

    def get_instance_types_recurse(kb,frame,
                                   inference_level = Node._taxonomic,
                                   number_of_values = Node._all,
                                   kb_local_only_p = 0,
                                   checked_kbs = [],indent=""):
        #trayce([kb,frame,checked_kbs])
        orig_frame = frame
#        if not kb.frame_p(frame):
#            (frame, frame_found_p) = kb.get_frame_in_kb(frame)
#            if not frame_found_p:
#                print "missing frame is",orig_frame
#                return ([],1,0)
#                raise GenericError,"frame '%s' not found" % str(frame)
        direct_types = kb.get_instance_types_internal(frame,
                                                      inference_level,
                                                      number_of_values,
                                                      kb_local_only_p)[0]

        if not kb_local_only_p:
            all_parents = kb.get_kb_parents()
            #print "all_parents",all_parents
            for kaybee in all_parents:
                #print "   asking",kaybee
                typs = kaybee.get_instance_types_internal(frame,
                                                          inference_level,
                                                          number_of_values,
                                                          kb_local_only_p)[0]
                for typ in typs:
                    if not (typ in direct_types):
                        #print "     appending instance_type",typ
                        direct_types.append(typ)

        taxonomic_types = [] #+ direct_types
        if inference_level in [Node._taxonomic,Node._all]:
            for dclass in direct_types:
                #if str(dclass) == 'Emits_ps': print "doing",dclass
                if not (dclass in taxonomic_types):
                    #print "     appending direct_type",dclass
                        
                    taxonomic_types.append(dclass)
                    supers = kb.get_class_superclasses(dclass,
                                                       inference_level=\
                                                       Node._taxonomic)[0]
                    for super in supers:
                        if not (super in taxonomic_types):
                            taxonomic_types.append(super)
        for typ in direct_types:
            if not (typ in taxonomic_types):
                taxonomic_types.append(typ)

        return (taxonomic_types,1,0)


    def get_kb_behaviors_internal(kb):
        return kb._behavior_values.keys()
    get_kb_behaviors = get_kb_behaviors_internal

    def get_kb_direct_parents(kb):
        return kb._parent_kbs

    def get_kb_direct_children(kb):
        meta = kb.connection().meta_kb()
        children = []
        for k in meta.get_kbs():
            if kb in k.get_kb_direct_parents():
                if not (k in children):
                    children.append(k)
        return children

    def get_kb_classes(kb,selector=Node._system_default,kb_local_only_p=0,
                       checked_kbs=[]):
        classes = kb.get_kb_classes_internal(selector,kb_local_only_p)
        if kb_local_only_p: return classes

        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for klass in parent.get_kb_classes(selector,
                                                   0,
                                                   checked_kbs):
                    if not (klass in classes):
                        classes.append(klass)
        return classes

    def get_kb_frames(kb, kb_local_only_p = 0):
        return kb.get_kb_frames_recurse(kb_local_only_p,[])

    def get_kb_frames_recurse(kb, kb_local_only_p = 0,
                      checked_kbs = []):
        # NOTE this is different from other get_kb_TYPE methods, no selector
        #print "get_kb_frames(kb=",str(kb),\
        #      ",kb_local_only_p=",kb_local_only_p,\
        #      ",checked_kbs=",checked_kbs,")"
        frames = kb.get_kb_frames_internal(1)
        if kb_local_only_p: return frames
        #print "  parents = ",kb.get_kb_direct_parents()        
        for parent in kb.get_kb_direct_parents():
            #print "  about to check parent:",parent  
            #print "    checked_kbs:",checked_kbs
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for frame in parent.get_kb_frames_recurse(0,
                                                          checked_kbs):
                    if not (frame in frames):
                        frames.append(frame)
        return frames

    def get_kb_facets(kb,selector=Node._system_default,
                           kb_local_only_p = 0,
                           checked_kbs = []):
        facets = kb.get_kb_facets_internal(selector,1)
        if kb_local_only_p: return facets

        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for facet in parent.get_kb_facets(selector,
                                                  0,
                                                  checked_kbs):
                    if not (facet in facets):
                        facets.append(facet)
        return facets

    def get_kb_individuals(kb,selector=Node._system_default,
                           kb_local_only_p = 0,
                           checked_kbs = []):
        individuals = kb.get_kb_individuals_internal(selector,1)
        if kb_local_only_p: return individuals

        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for individual in parent.get_kb_individuals(selector,
                                                            0,
                                                            checked_kbs):
                    if not (individual in individuals):
                        individuals.append(individual)
        return individuals

    def get_kb_parents(kb): # FIXME not in OKBC spec
        if not hasattr(kb,'_cached_kb_parents'):
            kb._cached_kb_parents = kb.get_kb_parents_recurse([])
        return kb._cached_kb_parents

    def get_kb_parents_recurse(kb,checked_kbs=[]):
        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for gran in parent.get_kb_parents_recurse(checked_kbs):
                    if not (gran in checked_kbs):
                        checked_kbs.append(gran)
        return checked_kbs

    def get_kb_slots(kb,selector=Node._system_default,
                           kb_local_only_p = 0,
                           checked_kbs = []):
        slots = kb.get_kb_slots_internal(selector,1)
        if kb_local_only_p: return slots

        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for slot in parent.get_kb_slots(selector,
                                                  0,
                                                  checked_kbs):
                    if not (slot in slots):
                        slots.append(slot)
        return slots

    def get_slot_facets(kb,frame,slot,
                       inference_level = Node._taxonomic,
                       slot_type = Node._own,
                       kb_local_only_p = 0):
        klop = kb_local_only_p
        il = inference_level
        (frame, frame_found_p) = kb.get_frame_in_kb(frame)
        (slot,  slot_found_p)  = kb.get_frame_in_kb(slot)
        kb_gsfi = kb.get_slot_facets_internal
        (list_of_facets,exact_p) = kb_gsfi(frame,slot,il,slot_type,klop)
        if inference_level in [Node._all,Node._taxonomic] and \
           slot_type in [Node._template,Node._all]:
            number_of_values = Node._all
            for klass in kb.get_instance_types(frame,il,
                                               number_of_values,klop):
                for facet in kb.get_slot_facets(klass,
                                                inference_level = il,
                                                slot_type=Node._template,
                                                kb_local_only_p = klop):
                    if not (facet in list_of_facets):
                        list_of_facets.append(facet)
        return (list_of_facets,exact_p)

    def get_slot_value(kb,frame,slot,
                       inference_level = Node._taxonomic,
                       slot_type = Node._own,
                       value_selector = Node._either,
                       kb_local_only_p = 0):
        number_of_values = 1
        r = kb.get_slot_values(frame,slot,
                               inference_level,slot_type,
                               number_of_values,value_selector,
                               kb_local_only_p)
        #print "r",r
        (list_of_values,exact_p,more_status) = r
        if len(list_of_values) > 1 or more_status:
            #print slot,frame,list_of_values,len(list_of_values),more_status
            raise CardinalityViolation,\
                  "slot '%s' on frame '%s' has > 1 value" % (slot,frame)
        value = None
        if list_of_values:
            value = list_of_values[0]
        return (value,exact_p)

    def get_slot_values(kb,frame,slot,
                        inference_level = Node._taxonomic,
                        slot_type = Node._own,
                        number_of_values = Node._all,
                        value_selector = Node._either,
                        kb_local_only_p = 0):
        
        kb_gsvid = kb.get_slot_values_in_detail
        (list_of_specs,exact_p,
         more_status,default_p) = kb_gsvid(frame,slot,
                                           inference_level,
                                           slot_type,
                                           number_of_values,
                                           value_selector,
                                           kb_local_only_p)
        list_of_values = map(lambda x:x[0],list_of_specs)
        return (list_of_values,exact_p,more_status)


    def CACHING_get_slot_values_in_detail(kb,frame,slot,
                                  inference_level = Node._taxonomic,
                                  slot_type = Node._own,
                                  number_of_values = Node._all,
                                  value_selector = Node._either,
                                  kb_local_only_p = 0):
        if not hasattr(kb,'_cached_get_slot_values_in_detail'):
            kb._cached_get_slot_values_in_detail = {}
        cache_key = str(frame) + str(slot) + str(slot_type) + \
                    str(number_of_values) + str(value_selector) +\
                    str(kb_local_only_p)
        cached_values = kb._cached_get_slot_values_in_detail.get(cache_key)
        if cached_values == None:
            checked_kbs = []
            checked_classes = []
            cached_values =  kb.get_slot_values_in_detail_recurse(frame,slot,
                                                    inference_level,
                                                    slot_type,
                                                    number_of_values,
                                                    value_selector,
                                                    kb_local_only_p,
                                                    checked_kbs,
                                                    checked_classes)
            kb._cached_get_slot_values_in_detail[cache_key] = cached_values
        return cached_values

    def get_slot_values_in_detail(kb,frame,slot,
                                  inference_level = Node._taxonomic,
                                  slot_type = Node._own,
                                  number_of_values = Node._all,
                                  value_selector = Node._either,
                                  kb_local_only_p = 0): #, checked_kbs=[],checked_classes=[]):
        checked_kbs = []
        checked_classes = []
        return kb.get_slot_values_in_detail_recurse(frame,slot,
                                                    inference_level,
                                                    slot_type,
                                                    number_of_values,
                                                    value_selector,
                                                    kb_local_only_p,
                                                    checked_kbs,
                                                    checked_classes)

    def get_slot_values_in_detail_recurse(kb,frame,slot,
                                          inference_level = Node._taxonomic,
                                          slot_type = Node._own,
                                          number_of_values = Node._all,
                                          value_selector = Node._either,
                                          kb_local_only_p = 0,
                                          checked_kbs=[],checked_classes=[]):
        #trayce((kb,frame,slot))
        (list_of_specs,exact_p,more_status,default_p) =\
           kb.get_slot_values_in_detail_internal(frame,slot,
                                                 inference_level,
                                                 slot_type,
                                                 number_of_values,
                                                 value_selector,
                                                 kb_local_only_p=1)
        #if str(frame) == 'docbook2ps':
        #    print kb,"list_of_specs",list_of_specs
        #trayce((list_of_specs),indent='   ')
        if inference_level in [Node._taxonomic,Node._all] \
           and slot_type != Node._own:
            my_types = kb.get_instance_types(frame,
                              inference_level=inference_level)[0]
            #print "all my_types",my_types
            for klass in my_types :
                #print "checking klass",klass
                if klass in checked_classes:
                    continue
                checked_classes.append(klass) #CLASS_RECURSION
                if klass == frame:
                    continue
                # should kb_local_only_p ignore template values outside of kb?
                if kb_local_only_p \
                   and not kb.frame_in_kb_p(klass,kb_local_only_p=1):
                    continue
                kb_gsvidr = kb.get_slot_values_in_detail_recurse
                #trayce((klass),format=" still about to check %s",indent='')
                for spec in kb_gsvidr(klass,
                                      slot,
                                      inference_level,
                                      Node._template,#slot_type
                                      number_of_values,
                                      value_selector,
                                      kb_local_only_p,
                                      checked_kbs,
                                      checked_classes)[0]:
                    #if DEBUG: print "  val =",val
                    #if not (spec in list_of_specs):
                    spec[1]=0
                    list_of_specs.append(spec)

        if not kb_local_only_p:
            for kaybee in kb.get_kb_parents():
                #trayce([kaybee],indent="  ")
                kb_gsvidi = kaybee.get_slot_values_in_detail_internal
                list_of_specs.extend(kb_gsvidi(frame,slot,inference_level,
                                               slot_type,number_of_values,
                                               value_selector,
                                               kb_local_only_p)[0])

        uniquify_specs(list_of_specs)
        return (list_of_specs,exact_p,more_status,default_p)        
    
    def individual_p(kb,thing,kb_local_only_p = 0):
        return isinstance(thing,INDIVIDUAL)

    def instance_of_p(kb,thing,klass,
                      inference_level=Node._taxonomic,
                      kb_local_only_p=0):
        # FIXME instance_of_p speedup by caching get_instance_types or
        # FIXME instance_of_p speedup by scanning directly
        number_of_values = Node._all
        typs = kb.get_instance_types(thing,
                                     inference_level,
                                     number_of_values,
                                     kb_local_only_p)[0]
        typs_str = map(str,typs)
        isit = str(klass) in typs_str
        return (isit,1)

    def print_frame(kb,frame,
                    slots = Node._filled,
                    facets = Node._filled,
                    stream = 1,
                    inference_level = Node._taxonomic,
                    number_of_values = Node._all,
                    value_selector = Node._either,
                    kb_local_only_p = 0):
        (frame,frame_found_p) = kb.get_frame_in_kb(frame)
        if not frame_found_p:
            out =  "frame '"+str(frame)+"' not found"
            print out
            raise 'bogusError'
            return out
        sentences = kb.get_frame_sentences(frame,
                                 value_selector=Node._known_true)[0]
        out = string.join(sentences,"\n")
        if stream:
            print out
            return None
        else:
            return out

    def put_direct_parents(kb,parent_kbs):
        if hasattr(kb,'_cached_kb_parents'):
            del kb['_cached_kb_parents']

        #if hasattr(kb,'_cached_get_instance_types'):
        #    del kb['_cached_get_instance_types']

        for parent in parent_kbs:
            if not kb_p(parent):
                parent = open_kb(parent)
                kb._parent_kbs.append(parent)

    def put_frame_pretty_name(kb,frame,name,kb_local_only_p=0):
        kb.put_frame_pretty_name_internal(frame,name,kb_local_only_p)

    def put_instance_types(kb,frame,new_types,kb_local_only_p = 0):
        klop = kb_local_only_p
        new_direct_types = []
        orig_types = kb.get_instance_types(frame,
                                           inference_level=Node._direct,
                                           kb_local_only_p = klop)
        for new_type in new_types:
            if isinstance(new_type,KLASS): # FIXME sigh
                new_direct_types.append(new_type)
            else:
                resp = kb.coerce_to_class(new_type,
                                          kb_local_only_p=klop)
                if resp[1]:
                    new_class = resp[0]
                    new_direct_types.append(new_class)                    
        frame._direct_types = new_direct_types

    def slot_p(kb,thing,kb_local_only_p=0):
        return isinstance(thing,SLOT)

Node._kb = KB(':kb')
Node._kb._frame_type = Node._class
KB._frame_type = Node._kb
KB._direct_types = [Node._KB]
Node._cache_types              = Node._frame_types + (Node._kb,)

class NullMetaKb(KB):
    """An empty meta_kb to work with NullConnection."""
    def _add_frame_to_cache(null_meta_kb,frame):
        pass
    def get_kbs(null_meta_kb):
        return []
    
class TupleKb(KB,Constrainable):
    """A simple in-RAM kb which has no saving or reading ability.
    
    Saving and reading ability can be left to subclasses. """
    def __init__(self,name='',connection=None):
        KB.__init__(self,name,connection=connection)
        self._cache = {}
        self._typed_cache = {}
        for frame_type in Node._cache_types:
            self._typed_cache[frame_type] = []

    def _add_frame_to_cache(kb,frame):
        frame_name = kb.get_frame_name(frame)
        frame_type = kb.get_frame_type(frame)
#        print "_add_frame_to_cache",frame_name
        if not kb._cache.has_key(frame_name):
            #print "caching",frame,frame_name
            kb._cache[frame_name] = frame
            kb._typed_cache[frame_type].append(frame)
            #print kb._name,kb._typed_cache
        else:
            warn("_add_frame_to_cache duplicate call for "+frame_name)
            # silently pass over any attempted duplication
            pass

    def add_class_superclass(kb,klass,new_superclass,
                             kb_local_only_p = 0):
        if new_superclass not in klass._direct_superclasses:
            klass._direct_superclasses.append(new_superclass)

    def class_p(kb,thing,kb_local_only_p = 0):
        return isinstance(thing,KLASS)

    def coerce_to_frame_internal(kb,frame):
        if str(kb) == str(frame):
            return kb
        return kb._cache.get(frame)

    def frame_in_kb_p_internal(kb,thing,
                               kb_local_only_p = 0):
        return kb._cache.has_key(str(thing))

    def get_class_subclasses_internal(kb,klass,
                                      inference_level = Node._taxonomic,
                                      number_of_values = Node._all,
                                      kb_local_only_p = 0):
        subclasses = []
        #trayce((kb,klass))
        #print kb._name,kb._typed_cache
        klass = kb.get_frame_in_kb(str(klass))[0]
        if klass != None:

            for a_class in kb._typed_cache[Node._class]:
                #trayce((klass,a_class),format="does %s == %s ?",indent=" ")
                #if str(a_class) == 'gear':trayce([kb,klass,a_class],indent="YOW ")
                if kb.subclass_of_p(a_class,klass,inference_level,
                                    kb_local_only_p):
                    subclasses.append(a_class)
        #trayce([subclasses],indent="    ")
        return (subclasses,1,0)
    
    def get_class_superclasses_internal(kb,klass,
                                        inference_level = Node._taxonomic,
                                        number_of_values = Node._all,
                                        kb_local_only_p = 0):
        if inference_level == Node._direct:
            return (copy.copy(klass._direct_superclasses),1,0)
        supers = []
        kb.get_class_superclasses_recurse(klass,supers)
        return (supers,1,0)

    def get_class_superclasses_recurse(kb,klass,supers):
        for super in klass._direct_superclasses:
            if not (super in supers):
                supers.append(super)
                kb.get_class_superclasses_recurse(super,supers)

    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0):
        found_frame = kb._cache.get(str(thing))
        if not found_frame:
            if thing == kb or str(thing) == str(kb):
                found_frame = kb
        # FIXME the whole coercibility issue is ignored
        if found_frame:
            return (found_frame,found_frame != None)
        else:
            return (None,None)

    def get_frame_pretty_name_internal(kb,frame,kb_local_only_p=0):
        found_frame = kb.get_frame_in_kb(frame)[0]
        if found_frame == None:
            return None
        else:
            return found_frame._pretty_name

    def get_frame_slots_internal(kb,frame,
                                 inference_level = Node._taxonomic,
                                 slot_type = Node._all,
                                 kb_local_only_p = 0):
        retarray = []
        slot_name = ''
        if slot_type in [Node._all,Node._own]:
            #print frame,slot_type,type(frame)
            for slot_name in frame._own_slots.keys():
                retarray.append(slot_name)
        if slot_type in [Node._all,Node._template]:
            for slot_name in frame._template_slots.keys():
                if not (slot_name in retarray):
                    retarray.append(slot_name)
        return (retarray,1)

    def get_frame_type(kb,thing,kb_local_only_p=0):
        if thing:
            return thing._frame_type
            if isinstance(thing,KB):
                return Node._kb  # FIXME
            elif isinstance(thing,FRAME):
                return thing.get_frame_type()
        else:
            return 0

    def get_instance_types_internal(kb,frame,
                                   inference_level = Node._taxonomic,
                                   number_of_values = Node._all,
                                   kb_local_only_p = 0):
        #if str(kb) == "common_transformers": print "we are in ",kb
        frame=kb.get_frame_in_kb_internal(str(frame))[0]
        if frame:
            return (copy.copy(frame._direct_types),1,0)
        return ([],1,0)

    
    def get_kb_classes_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._class, kb_local_only_p)

    def get_kb_facets_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._facet, kb_local_only_p)

    def get_kb_frames_internal(kb,selector=Node._system_default,
                               kb_local_only_p=None):
        return copy.copy(kb._cache.values())

    def get_kb_individuals_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._individual,kb_local_only_p)

    def get_kb_slots_internal(kb,selector=Node._system_default,
                              kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._slot,kb_local_only_p)

    def get_kb_frames_by_type(kb, frame_type,
                              selector = Node._system_default,
                              kb_local_only_p=None):
        return copy.copy(kb._typed_cache[frame_type])

    def get_kbs(kb):
        return kb.get_kb_frames_by_type(Node._kb)

    def get_slot_facets_internal(kb,frame,slot,
                                 inference_level = Node._taxonomic,
                                 slot_type = Node._own,
                                 kb_local_only_p = 0):
        retarray = []
        slot_name = ''
        if slot_type in [Node._all,Node._own]:
            unit_slot = frame._own_slots.get(slot)
            if unit_slot:
                for facet_name in unit_slot.facets().keys():
                    retarray.append(facet_name)
        if slot_type in [Node._all,Node._template]:
            unit_slot = frame._template_slots.get(slot)
            if unit_slot:
                for facet_name in unit_slot.facets().keys():
                    retarray.append(facet_name)
        return (retarray,1)

    def get_slot_values_in_detail_internal(kb,frame,slot,
                                          inference_level = Node._taxonomic,
                                          slot_type = Node._own,
                                          number_of_values = Node._all,
                                          value_selector = Node._either,
                                          kb_local_only_p = 0,
                                          checked_kbs=[],checked_classes=[]):
        #trayce((kb,frame,slot,type(slot),slot_type))
        orig_frame = frame
        (list_of_specs,exact_p,more_status,default_p) = ([],1,0,0)
        frame = kb.coerce_to_frame_internal(str(frame))
        if not frame:
            #print "bailing on",orig_frame,"in",kb
            return [[],1,0,1]
#        print "gsvidi(",kb,frame,")"
#        if str(kb) == 'nooron_pattern_language_data' and \
#           str(frame) == 'DontRepeat':
#            raise youch, booger
        slot_key = str(slot)
        
        #print "gsvidi",frame,frame.__class__.__bases__,slot
        #if 'KB' in frame.__class__.__bases__:
        #    print "get_slot_values_in_detail_internal",frame
        #print str(frame)
        #if str(frame) == 'smurp_web_log.pykb':
        #    print "get_slot_values_in_detail_internal",frame
        if slot_type in [Node._own,Node._all]:
            if frame._own_slots.has_key(slot_key):
                for v in frame._own_slots[slot_key].values():
                    list_of_specs.append([v,1,0])
        if slot_type in [Node._template,Node._all]:
            if frame._template_slots.has_key(slot_key):
                for v in frame._template_slots[slot_key].values():
                    list_of_specs.append([v,1,0])
        return (list_of_specs,exact_p,more_status,default_p)

    def OLD_get_slot_values_internal(kb,frame,slot,
                                 inference_level = Node._taxonomic,
                                 slot_type = Node._own,
                                 number_of_values = Node._all,
                                 value_selector = Node._either,
                                 kb_local_only_p = 0):
        kb_gsvidi = kb.get_slot_values_in_detail_internal
        (list_of_specs,exact_p,
         more_status,default_p) = kb_gsvidi(frame,slot,
                                            inference_level,
                                            slot_type,
                                            number_of_values,
                                            value_selector,
                                            kb_local_only_p)
        print "  list_of_specs",list_of_specs
        list_of_values = map(lambda x:x[0],list_of_specs)
        #print list_of_values,list_of_specs
        return (list_of_values,exact_p,more_status)


    def OOOLD_get_slot_values_internal(kb,frame,slot,
                                 inference_level = Node._taxonomic,
                                 slot_type = Node._own,
                                 number_of_values = Node._all,
                                 value_selector = Node._either,
                                 kb_local_only_p = 0):
        list_of_values = []
        exact_p = 0
        slot_key = str(slot)
        #slot_key = slot
        #for k in frame._own_slots.keys(): print "  key",k,type(k)
            
        if slot_type in [Node._own,Node._all]:
            if frame._own_slots.has_key(slot_key):
                list_of_values.extend(frame._own_slots[slot_key].values())
        if slot_type in [Node._template,Node._all]:
            if frame._template_slots.has_key(slot_key):
                list_of_values.extend(frame._template_slots[slot_key].values())
        return (list_of_values,exact_p,0)

    def put_class_superclasses(kb,klass,new_superclasses,
                               kb_local_only_p = 0):
        klop = kb_local_only_p
        new_direct_superclasses = []
        #orig_superclasses =
        for new_super in new_superclasses:
            if isinstance(new_super,KLASS): # FIXME sigh
                new_direct_superclasses.append(new_super)
            else:
                resp = kb.coerce_to_class(new_super,
                                          kb_local_only_p=klop)
                if resp[1]:
                    new_class = resp[0]
                    new_direct_superclasses.append(new_class)
        klass._direct_superclasses = new_direct_superclasses

    def put_frame_pretty_name_internal(kb,frame,name,kb_local_only_p=0):
        (found_frame,
         frame_found_p) = kb.get_frame_in_kb(frame,
                                             kb_local_only_p=0)
        if found_frame:
            found_frame._pretty_name = name
        # FIXME put_frame_pretty_name_internal should raise frame_not_found

    def put_slot_value(kb,frame,slot, value,
                       slot_type=Node._own,
                       value_selector = Node._known_true,
                       kb_local_only_p = 0):
        """Sets the values of slot in frame to be a singleton set
        consisting of a single element: value.  This operation may
        signal constraint violation conditions (see Section 3.8).
        Returns no values. """
        if type(value) == type([]): raise CardinalityViolation,str(value)
        (frame,frame_found_p) = kb.get_frame_in_kb(frame)
        (slot,slot_found_p) = kb.get_frame_in_kb(slot)
        slot_key = str(slot)
        if slot_type == Node._own:
            #print "got to here",frame,slot,slot_type
            if frame._own_slots.has_key(slot_key):
                frame._own_slots[slot_key].set_value(value)
            else:
                frame._own_slots[slot_key] = UNIT_SLOT(slot,value)
        elif slot_type == Node._template:
            if frame._template_slots.has_key(slot_key):
                frame._template_slots[slot_key].set_value(value)
            else:
                frame._template_slots[slot_key] = UNIT_SLOT(slot,value)
        

    def put_slot_values(kb,frame,slot, values,
                        slot_type=Node._own,
                        value_selector = Node._known_true,
                        kb_local_only_p = 0):
        (frame,
         frame_found_p) = kb.get_frame_in_kb(frame,
                                             kb_local_only_p=0)
        if not frame:
            return 

        if type(values) != type([]): raise CardinalityViolation(values)
        slot_key = str(slot)

        kb_get_behave = kb.get_behavior_values_internal
        if Node._immediate in kb_get_behave(Node._constraint_checking_time):
            current_values = kb.get_slot_values(frame,slot,
                                                inference_level = Node._all,
                                                slot_type = Node._own,
                                                number_of_values = Node._all,
                                                value_selector = Node._either,
                                                kb_local_only_p = 0)
            orig_values = copy.copy(values)
            values = kb.enforce_slot_constraints(frame,slot,
                                                 current_values = current_values,
                                                 future_values = values,
                                                 inference_level = Node._all,
                                                 slot_type = Node._either,
                                                 kb_local_only_p = 0)
            if len(orig_values) <> len(values):
                print "We got shortened."

        #if 'snargle' in values:
        #    print "put_slot_values(",kb,frame,slot,values,")"            
        if slot_type == Node._own:
            if frame._own_slots.has_key(slot_key):
                frame._own_slots[slot_key].set_values(values)
            else:
                frame._own_slots[slot_key] = UNIT_SLOT(slot,values)
        elif slot_type == Node._template:
            if frame._template_slots.has_key(slot_key):
                frame._template_slots[slot_key].set_values(values)
            else:
                frame._template_slots[slot_key] = UNIT_SLOT(slot,values)

    def subclass_of_p(kb,subclass,superclass,
                      inference_level=Node._taxonomic,
                      kb_local_only_p = 0):
        return kb.superclass_of_p(superclass,subclass,inference_level)

    def superclass_of_p(kb,superclass,subclass,
                        inference_level=Node._taxonomic):
        supers = kb.get_class_superclasses(subclass,inference_level)

        return superclass in supers[0]

class AbstractPersistentKb(TupleKb):
    """PersistentKb implements save_kb and save_kb_as to someplace.."""
    def save_kb(kb,error_p = 1):
        filename = kb.get_frame_name(kb)
        kb._save_to_storage(filename,error_p=error_p)

    def save_kb_as(kb,new_name_or_locator,error_p = 1):
        if type(new_name_or_locator) != type(''):
            raise 'NotStoragePath', \
                  str(new_name_or_locator) + " not a storage path"
        filename = new_name_or_locator
        kb._save_to_storage(filename,error_p=error_p)

    def _print_kb(kb):
        for frame in \
            get_kb_facets(kb) + \
            get_kb_slots(kb) + \
            get_kb_classes(kb) + \
            get_kb_individuals(kb):
            kb.print_frame(frame,stream=1)

class PrimordialKb(TupleKb):
    """Implements synthetic :DOCUMENTATION slot values which are URLs
    pointing at the OKBC Spec."""
    def __init__(self,name='',connection=None):
        null_connection = NullConnection()
        TupleKb.__init__(self,name,connection=null_connection)

    def get_frame_slots_internal(kb,frame,
                                 inference_level = Node._taxonomic,
                                 slot_type = Node._all,
                                 kb_local_only_p = 0):
        apkb_gfsi = AbstractPersistentKb.get_frame_slots_internal
        (list_of_slots,exact_p) = apkb_gfsi(kb,frame,inference_level,
                                            slot_type,kb_local_only_p)
        if not (':DOCUMENTATION' in list_of_slots):
            list_of_slots.append(':DOCUMENTATION')
        return (list_of_slots,exact_p)
            
    def get_slot_values_in_detail_internal(kb,frame,slot,
                                          inference_level = Node._taxonomic,
                                          slot_type = Node._own,
                                          number_of_values = Node._all,
                                          value_selector = Node._either,
                                          kb_local_only_p = 0,
                                          checked_kbs=[],checked_classes=[]):
        if kb.coerce_to_frame_internal(str(frame)):
            if str(slot) == ':DOCUMENTATION' and \
               str(frame) != 'PRIMORDIAL_KB':
                #FIXME more generally skip things which are not in OKBC Spec
                # list-of-specs,exact-p,more-status,default-p
                return ([[get_doc_for(frame),1,0]],1,0,0)
        apkb_gsvidi = AbstractPersistentKb.get_slot_values_in_detail_internal
        return apkb_gsvidi(kb,frame,slot,
                           inference_level,slot_type,
                           number_of_values,
                           value_selector,
                           kb_local_only_p,
                           checked_kbs,checked_classes)

    
class AbstractFileKb(AbstractPersistentKb):
    
    def _save_to_storage(kb,filename,error_p = 1):
        print "saving to",filename
        outfile = open(filename,"w")
        for frame in \
            get_kb_facets(kb) + \
            get_kb_slots(kb) + \
            get_kb_classes(kb) + \
            get_kb_individuals(kb):
            outfile.write(kb.print_frame(frame,stream=0))
        outfile.close()


class Connection: #abstract
    def __init__(connection,initargs=None):
        # This code never gets called (because Connection is abstract)
        # but in subclasses it should do something like the following:
        connection._meta_kb = META_KB('DefaultMetaKb',
                                      connection = connection)
        from PyKb import PyKb
        connection._default_kb_type = PyKb

    def create_kb(connection,
                  kb_type=None,
                  kb_locator=None,
                  initargs={}):
        if not kb_type:
            kb_type = connection._default_kb_type
        my_meta_kb = connection._meta_kb
        
        kb = kb_type(kb_locator,initargs=initargs,
                     meta=my_meta_kb)
        my_meta_kb._add_frame_to_cache(kb)
        return kb

    def find_kb(connection,name_or_kb_or_kb_locator):
        meta = connection.meta_kb()
        return meta.get_frame_in_kb(name_or_kb_or_kb_locator)[0]

    def meta_kb(connection):
        return connection._meta_kb

    def open_kb(connection, kb_locator, kb_type = None, error_p = 1):
        if not kb_type:
            kb_type = connection._default_kb_type
        my_meta_kb = kb=connection._meta_kb
        (kb,frame_found_p) = kb.get_frame_in_kb(kb_locator,error_p)
        if not kb:
            kb = kb_type(kb_locator,connection=connection)
            my_meta_kb._add_frame_to_cache(kb)
        return kb

    def openable_kbs(connection, kb_type = None, place = None):
        warn("Connection.openable_kbs is abstract",20)
        return []
    
##    def all_connections
##    def close_connection
##    def establish_connection

class NullConnection(Connection):
    def __init__(connection,initargs=None):
        connection._meta_kb = None # so NullMetaKb can grab it!
        connection._meta_kb = NullMetaKb('NullMetaKb',
                                         connection=connection)
        connection._default_kb_type = None

class UNIT_SLOT:
    """UNIT_SLOT is the structure which holds the facets and the values
    for a slot on a particular frame."""
    def __init__(self,slot_unit,values=[],facets=[]):
        self._slot_unit = slot_unit
        if type(values) != type([]): values = [values]        
        self._values = values
        if type(facets) != type([]): facets = [facets]
        self._facets = facets
    def __repr__(self):
        return str(self._values)
    def facets(self):
        return self._facets
    def set_facet(self,facet):
        self._facets = [facet]
    def set_facets(self,facets):
        self._facets = facets
    def values(self):
        return self._values
    def set_value(self,value):
        self._values = [value]
    def set_values(self,values):
        self._values = values


##########################################
#    Utils
##########################################    

def dump_kb(kb):
    for frame in get_kb_frames(kb=kb):
        dump_frame(frame,kb=kb)
        print ""

def dump_frame(frame,kb=None):
    kb = current_kb()
    (frame,frame_found_p) = kb.get_frame_in_kb(frame)
    if not frame:
        print frame,"not found"
        return 

    print get_frame_name(frame),"("+str(get_frame_type(frame))+")"
    for klass in get_instance_types(frame,kb=kb,
                                    inference_level=Node._all)[0]:
        print "  Class:", klass
    if kb.class_p(frame):
        for super in get_class_superclasses(frame, kb=kb,
                                            inference_level=Node._all)[0]:
            print "  Superclass:", super
    for slot in get_frame_slots(frame)[0]:
        print "  Slot:", slot
        print "     values: "+\
              str(get_slot_values(frame,slot,
                                  inference_level = Node._all,
                                  slot_type=Node._all)[0])
    #print "own_slots:",frame._own_slots        
    #print "template_slots:",frame._template_slots


def get_doc_for(thing):
    link_text = "docs for "+str(thing)
    nom = str(thing)
    if type(thing) == type(get_doc_for):
        nom = thing.__name__
        link_text = thing.__name__
    nom = string.replace(nom,'_','-')
    return """<a target="okbcdocs" href="%s">%s</a>""" % \
           (OKBC_SPEC_BASE_URL + nom,link_text)
    

##########################################
#    Okbc methods
##########################################

from Funcs import *

##########################################
#    PrimorialKB
##########################################

#Node._primordial_kb = AbstractPersistentKb('PRIMORDIAL_KB')
Node._primordial_kb = PrimordialKb('PRIMORDIAL_KB')
goto_kb(Node._primordial_kb)
PRIMORDIAL_KB = Node._primordial_kb

for f in primordials:
    Node._primordial_kb._add_frame_to_cache(f)
    
