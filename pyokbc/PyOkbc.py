
WARNINGS = 2
# 10 critical
# 20 noops
# 30 subtleties
PRIMORDIAL_KB = ()
OKBC_SPEC_BASE_URL =  "http://www.ai.sri.com/~okbc/spec/okbc2/okbc2.html#"

import string
import copy
import os

from  OkbcConditions import *

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

    def __repr__(self):
        return str(self)


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

Node._slot = FACET(':slot')
Node._slot._frame_type = Node._class
SLOT._frame_type = Node._slot

Node._individual = FACET(':individual')
Node._individual._frame_type = Node._class
INDIVIDUAL._frame_type = Node._individual

Node._kb = FACET(':kb')
Node._kb._frame_type = Node._class


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

Node._all                      = Symbol(':all')
Node._own                      = Symbol(':own')
Node._template                 = Symbol(':template')
Node._slot_types               = (Node._all,Node._template,Node._own)
    
Node._taxonomic                = Symbol(':taxonomic')
Node._direct                   = Symbol(':direct')
Node._inference_levels         = (Node._taxonomic,Node._all,Node._direct)
    
Node._default_only             = Symbol(':default-only')
Node._known_true               = Symbol(':known-true')
Node._either                   = Symbol(':either')
Node._value_selectors          = (Node._either,Node._default_only,Node._known_true)
    
Node._more                     = Symbol(':more')
Node._number_of_values         = (Node._all,Node._more)


#Node._kb                       = Symbol(':kb') # not included in _frame_types
Node._frame_types              = (Node._class,Node._individual,Node._slot,Node._facet)
Node._cache_types              = Node._frame_types + (Node._kb,)
    
Node._value                    = Symbol(':value')
Node._frame                    = Symbol(':frame')
Node._target_contexts          = (Node._frame,Node._slot,Node._facet,Node._class,Node._individual,Node._value)
    
Node._system_default           = Symbol(':system-default')
Node._frames                   = Symbol(':frames')
Node._selector_all             = (Node._all,Node._frames,Node._system_default)
Node._default                  = Symbol(':default')

Node._filled                   = Symbol(':filled')

    # initargs
Node._port                     = Symbol(':port')
Node._host                     = Symbol(':host')
Node._password                 = Symbol(':password')
Node._username                 = Symbol(':username')
Node._parent_kbs               = Symbol(':parent-kbs')

# standard slots
#Node._DOCUMENTATION            = primordialSLOT(":DOCUMENTATION")

primordial = {}

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
                       ":NUMBER",":INTEGER",":STRING",
                       ":SEXPR",":SYMBOL",":LIST")

primordial['individual'] = ()

Node._THING = primordialKLASS(":THING")
Node._CLASS = primordialKLASS(":CLASS")

def bootstrap(primordial = primordial):
    types_in_order = ['facet','slot','class','individual']    
    types = (('facet',      primordialFACET),
             ('slot',       primordialSLOT),
             ('class',      primordialKLASS),
             ('individual', primordialINDIVIDUAL))
    for typ,construct in types:
        for name in primordial[typ]:
            pyname = name
            pyname = pyname.replace("-","_")
            pyname = pyname.replace(":","_")
            #print pyname,name
            Node.__dict__[pyname] = construct(name)
            if type == 'class':
                Node.__dict__[pyname].__direct_types = [Node._CLASS]
                Node.__dict__[pyname].__direct_superclasses = [Node._THING]

bootstrap()

Node._NUMBER._direct_superclasses.append(Node._INDIVIDUAL)
Node._INTEGER._direct_superclasses.append(Node._NUMBER)
Node._STRING._direct_superclasses.append(Node._INDIVIDUAL)
Node._SYMBOL._direct_superclasses.append(Node._SEXPR)
Node._LIST._direct_superclasses.append(Node._INDIVIDUAL)

    


    # behavior values
Node._never                    = Symbol(':never')
Node._immediate                = Symbol(':immediate')
Node._user_defined_facets      = Symbol(':user-defined-facets')
Node._facets_reported          = Symbol(':facets-reported')    
Node._read_only                = Symbol(':read-only')
Node._monotonic                = Symbol(':monotonic')
Node._deferred                 = Symbol(':deferred')
Node._background               = Symbol(':background')
Node._override                 = Symbol(':override')
Node._when_consistent          = Symbol(':when-consistent')
Node._none                     = Symbol(':none')
Node._list                     = Symbol(':list')
    
    # behaviors
Node._are_frames               = Symbol(':are-frames')
Node._are_frames_all           = (Node._class,Node._individual,Node._slot,Node._facet)
Node._class_slot_types         = Symbol(':class-slot-types')
Node._class_slot_types_all     = (Node._template, Node._own)
Node._collection_types         = Symbol(':collection-types')
Node._compliance               = Symbol(':compliance')
Node._compliance_all             = (Node._facets_reported,
                               Node._user_defined_facets,
                               Node._read_only,
                               Node._monotonic)
Node._constraints_checked      = Symbol(':constraints-checked')
Node._constraints_checked_all  = (Node._VALUE_TYPE,
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
                                  Node._DOCUMENTATION_IN_FRAME)
Node._constraint_checking_time = Symbol(':constraint-time-checking')
Node._constraint_checking_time_all = (Node._immediate,Node._deferred,Node._background,Node._never)
Node._constraint_report_time   = Symbol(':constraint-report-time')
Node._constraint_report_time_all = (Node._immediate,Node._deferred)
Node._defaults                 = Symbol(':defaults')
Node._defaults_all             = (Node._override,
                                  Node._when_consistent,
                                  Node._none)

Node._behaviours_all           = (Node._are_frames,
                                  Node._class_slot_types,
                                  Node._collection_types,
                                  Node._compliance,
                                  Node._constraints_checked,
                                  Node._constraint_checking_time,
                                  Node._constraint_report_time,
                                  Node._defaults)





class KB(FRAME):    
    """All OKBC methods which take a KB argument should be implemented here.
    The exceptions are the mandatory ones.  All of them are implemented in
    TupleKB.  That leaves all optional methods, which should be implemented
    here.  Oh I am sure this is all screwed up!"""
    _frame_type = Node._kb    
    __allow_access_to_unprotected_subobjects__ = 1
    def __init__(self,name,initargs = {},connection=None):
        if connection:
            kb = connection.meta_kb()
        else:
            kb = None
        self._connection = connection
        FRAME.__init__(self,name,frame_type=Node._kb,kb=kb)

        self._initargs = initargs
        
        parent_kbs = initargs.get(Node._parent_kbs,[])
        if PRIMORDIAL_KB: parent_kbs.append(PRIMORDIAL_KB) #FIXME not always!
        self._parent_kbs = parent_kbs # FIXME
    
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

        kb.put_instance_types(frame,direct_types,
                              kb_local_only_p = kb_local_only_p)

        # FIXME should use mandatory put-class-superclasses
        if direct_superclasses:
            kb.put_class_superclasses(frame,direct_superclasses,
                                      kb_local_only_p = klop)

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
                              doc,slot_type=Node._template,
                              kb_local_only_p=kb_local_only_p)
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

    def frame_p(kb,thing,kb_local_only_p = 0): # FIXME not in OKBC Spec
        return isinstance(thing,FRAME)


    _behaviour_values = {Node._are_frames : [Node._class,
                                             Node._individual,
                                             Node._slot,
                                             Node._facet],
                         Node._class_slot_types : [Node._template],
                         Node._collection_types : [Node._list],
                         Node._constraint_checking_time : [Node._never],
                         Node._constraint_report_time : [Node._never],
                         Node._constraints_checked : [],
                         Node._defaults : [Node._override]}

    def get_behaviour_values_internal(kb,behavior):
        return kb._behavior_values.get(behavior,[])
    get_behaviour_values = get_behaviour_values_internal

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
                #print frame,"is instance of",klass,"in",kb
        return (list_of_instances,exact_p,more_status)

    def get_class_instances(kb,klass,
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
        if not kb_local_only_p:
            for parent in kb.get_kb_direct_parents():
                if not (parent in checked_kbs):
                    checked_kbs.append(parent)
                    rets = parent.get_class_instances(klass,
                                                      inference_level,
                                                      number_of_values,
                                                      kb_local_only_p,
                                                      checked_kbs)
        return rets

    def get_class_subclasses(kb,klass,
                             inference_level = Node._taxonomic,
                             number_of_values = Node._all,
                             kb_local_only_p = 0,
                             checked_kbs=[]):
        (klass,class_found_p) = kb.coerce_to_class(klass)
        checked_kbs.append(kb)
        rets = kb.get_class_subclasses_internal(klass,
                                                inference_level,
                                                number_of_values,
                                                kb_local_only_p=1)
        warn('get_class_subclasses ignoring kb_local_only_p')
        #if not kb_local_only_p:
        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                rets = parent.get_class_subclasses(klass,
                                                   inference_level,
                                                   number_of_values,
                                                   kb_local_only_p,
                                                   checked_kbs)
        return rets

    def get_class_superclasses(kb,klass,
                               inference_level = Node._taxonomic,
                               number_of_values = Node._all,
                               kb_local_only_p = 0,
                               superclasses = []):
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
                superclasses.append(super)
                more_supers = kb.get_class_superclasses(super,
                                                        inference_level,
                                                        number_of_values,
                                                        kb_local_only_p)[0]
                #print "more_supers",super,more_supers
                for more_super in more_supers:
                    if not (more_super in superclasses):
                        superclasses.append(more_super)
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
        return frame._name
        #if isinstance(kb,KB):
        #    return frame._name
        #return frame.get_frame_name(kb_local_only_p=kb_local_only_p)
    get_frame_name = get_frame_name_internal

    def get_frame_pretty_name_internal(kb,frame,kb_local_only_p=0):
        #if isinstance(kb,META_KB):
        #    return frame._pretty_name
        return frame._pretty_name
    get_frame_pretty_name = get_frame_pretty_name_internal

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
            print "slot =",slot,slot.__class__,slot.__class__.__bases__
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
        klop = kb_local_only_p
        il = inference_level
        (frame,frame_found_p) = kb.get_frame_in_kb(frame)        
        (list_of_slots,
         exact_p) = kb.get_frame_slots_internal(frame,inference_level,
                                                slot_type,klop)
        if inference_level in [Node._all,Node._taxonomic] and \
           slot_type in [Node._template,Node._all]:
            for klass in kb.get_instance_types(frame, inference_level = il,
                                               number_of_values = Node._all,
                                               kb_local_only_p = klop)[0]:
                for slot in  kb.get_frame_slots(klass,
                                                inference_level = il,
                                                slot_type=Node._template,
                                                kb_local_only_p=klop)[0]:
                    if not (slot in list_of_slots):
                        list_of_slots.append(slot)
        return (list_of_slots,exact_p)

    def get_frame_type_internal(kb,thing,kb_local_only_p=0):
        return thing.get_frame_type()
    get_frame_type = get_frame_type_internal

    def get_instance_types_internal(kb,frame,
                                    inference_level = Node._taxonomic,
                                    number_of_values = Node._all,
                                    kb_local_only_p = 0):
        warn("get_instance_types ignores kb_local_only_p",20)
        if not kb.frame_p(frame):
            (frame, frame_found_p) = get_frame_in_kb(frame)
            if not frame_found_p:
                raise GenericError,"frame '%s' not found" % str(frame)
        taxonomic_types = []
        if inference_level in [Node._taxonomic,Node._all]:
            for dclass in frame._direct_types:
                if not (dclass in taxonomic_types):
                    taxonomic_types.append(dclass)
                    supers = kb.get_class_superclasses(dclass,
                                                       inference_level=\
                                                       Node._taxonomic)[0]
                    for super in supers:
                        if not (super in taxonomic_types):
                            taxonomic_types.append(super)
            return (taxonomic_types,1,0)
        else:
            return (copy.copy(frame._direct_types),1,0)
    get_instance_types = get_instance_types_internal

    def get_kb_behaviours_internal(kb):
        return kb._behavior_values.keys()
    get_kb_behaviours = get_kb_behaviours_internal

    def get_kb_direct_parents(kb):
        return kb._parent_kbs

    def get_kb_classes(kb,selector=Node._system_default,kb_local_only_p=0,
                       checked_kbs=[]):
        classes = kb.get_kb_classes_internal(selector,kb_local_only_p)
        if kb_local_only_p: return classes
        checked_kbs = []
        for parent in kb.get_kb_direct_parents():
            if not (parent in checked_kbs):
                checked_kbs.append(parent)
                for klass in parent.get_kb_classes(selector,
                                                   kb_local_only_p,
                                                   checked_kbs):
                    if not (klass in classes):
                        classes.append(klass)
        return classes

    def get_kb_frames(kb,kb_local_only_p=0):
        frames = kb.get_kb_frames_internal(0)
        if not kb_local_only_p:
            for parent in kb.get_kb_direct_parents():
                frames.extend(parent.get_kb_frames(1))
        return frames

    def get_slot_values(kb,frame,slot,
                        inference_level = Node._taxonomic,
                        slot_type = Node._own,
                        number_of_values = Node._all,
                        value_selector = Node._either,
                        kb_local_only_p = 0):
        """Returns the list-of-values of slot within frame.
        If the :collection-type of the slot is
        :list, and only :direct own slots have been asserted,
        then order is preserved; otherwise the values are returned in
        no guaranteed order. Get-slot-values always returns a list of
        values. If the specified slot has no values, () is returned.
        Return Value(s): list-of-values exact-p more-status 
        Flags: E O R """
        klop = kb_local_only_p
        il =  inference_level
        (found_frame,
         frame_found_p) = kb.get_frame_in_kb(frame,
                                             kb_local_only_p=klop)
        (found_slot,
         slot_found_p) = kb.get_frame_in_kb(slot,
                                            kb_local_only_p=klop)
        if not slot_found_p or not frame_found_p:
            #raise SlotNotFound,(frame,slot,slot_type,kb)
            return ([],0,0)

        (list_of_values,exact_p,more_status) = ([],0,0)

        kb_gsvi = kb.get_slot_values_internal
        (list_of_values,
         exact_p,
         more_status) = kb_gsvi(found_frame,
                                found_slot,
                                inference_level=inference_level,
                                slot_type = slot_type,
                                number_of_values = number_of_values,
                                value_selector = value_selector,
                                kb_local_only_p = kb_local_only_p)

        if inference_level in [Node._taxonomic,Node._all] and \
           slot_type != Node._own:
            my_types = kb.get_instance_types(found_frame,
                                             inference_level=il)[0]
            for klass in my_types:
                for val in kb.get_slot_values(klass,found_slot,
                                              inference_level=inference_level,
                                              slot_type=Node._template)[0]:
                    if not (val in list_of_values):
                        list_of_values.append(val)

        return (list_of_values,exact_p,more_status)

    def individual_p(kb,thing,kb_local_only_p = 0):
        return isinstance(thing,INDIVIDUAL)

    def instance_of_p(kb,thing,klass,
                      inference_level=Node._taxonomic,
                      kb_local_only_p=0):
        number_of_values = Node._all
        isit = klass in kb.get_instance_types(thing,
                                              inference_level,
                                              number_of_values,
                                              kb_local_only_p)[0]
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
        for parent in parent_kbs:
            if not kb_p(parent):
                parent = open_kb(parent)
                kb._parent_kbs.append(parent)

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


class TupleKb(KB):
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

    def get_class_subclasses_internal(kb,klass,
                                      inference_level = Node._taxonomic,
                                      number_of_values = Node._all,
                                      kb_local_only_p = 0):
        subclasses = []
        #print kb._name,kb._typed_cache
        for a_class in kb._typed_cache[Node._class]:
            if kb.subclass_of_p(a_class,klass,inference_level,
                                kb_local_only_p):
                subclasses.append(a_class)
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
        # FIXME the whole coercibility issue is ignored
        if found_frame:
            return (found_frame,found_frame != None)
        else:
            return (None,None)

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
    
    def get_kb_classes_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._class,
                                     kb_local_only_p = kb_local_only_p)

    def get_kb_facets_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._facet,
                                     kb_local_only_p = kb_local_only_p)

    def get_kb_frames_internal(kb,kb_local_only_p=None):
        return copy.copy(kb._cache.values())

    def get_kb_individuals_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._individual,
                                    kb_local_only_p = kb_local_only_p)

    def get_kb_slots_internal(kb,selector=Node._system_default,
                                kb_local_only_p = 0):
        return kb.get_kb_frames_by_type(Node._slot,
                                     kb_local_only_p = kb_local_only_p)
    get_kb_slots = get_kb_slots_internal

    def get_kb_frames_by_type(kb, frame_type,
                              selector = Node._system_default,
                              kb_local_only_p=None):
        return copy.copy(kb._typed_cache[frame_type])

    def frame_in_kb_p_internal(kb,thing,
                               kb_local_only_p = 0):
        return kb._cache.has_key(str(thing))
    frame_in_kb_p = frame_in_kb_p_internal

    def get_slot_values_internal(kb,frame,slot,
                                 inference_level = Node._taxonomic,
                                 slot_type = Node._own,
                                 number_of_values = Node._all,
                                 value_selector = Node._either,
                                 kb_local_only_p = 0):
        list_of_values = []
        exact_p = 0
        slot_key = str(slot)
        if slot_type in [Node._own,Node._all]:
            if frame._own_slots.has_key(slot_key):
                list_of_values.extend(frame._own_slots[slot_key].values())
        if slot_type in [Node._template,Node._all]:
            if frame._template_slots.has_key(slot_key):
                list_of_values.extend(frame._template_slots[slot_key].values())
        return (list_of_values,exact_p,Node._all)

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
        if slot_type == Node._own:
            if frame._own_slots.has_key(slot):
                frame._own_slots[slot].set_value(value)
            else:
                frame._own_slots[slot] = UNIT_SLOT(slot,value)
        elif slot_type == Node._template:
            if frame._template_slots.has_key(slot):
                frame._template_slots[slot].set_value(value)
            else:
                frame._template_slots[slot] = UNIT_SLOT(slot,value)

    def put_slot_values(kb,frame,slot, values,
                        slot_type=Node._own,
                        value_selector = Node._known_true,
                        kb_local_only_p = 0):
        """Sets the values of slot in frame to be a singleton set
        consisting of a single element: value.  This operation may
        signal constraint violation conditions (see Section 3.8).
        Returns no values. """
        if type(values) != type([]): raise CardinalityViolation(values)
        if slot_type == Node._own:
            if frame._own_slots.has_key(slot):
                frame._own_slots[slot].set_values(values)
            else:
                frame._own_slots[slot] = UNIT_SLOT(slot,values)
        elif slot_type == Node._template:
            if frame._template_slots.has_key(slot):
                frame._template_slots[slot].set_values(values)
            else:
                frame._template_slots[slot] = UNIT_SLOT(slot,values)

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


class Connection:
    def __init__(connection,initargs=None):
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
        warn("openable_kbs is a noop",20)
        return []
    
##    def all_connections
##    def close_connection
##    def establish_connection



class UNIT_SLOT:
    """UNIT_SLOT is the structure on a frame which holds the values
    and facets for a particular named slot.  That is in contrast
    with SlotUnit which is the python class which represents the 
    FRAME of type SLOT which exists in the KB."""

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

    
def warn(mess,level=10):
    if WARNINGS >= level:
        print mess

def get_doc_for(thing):
    text = ''
    if type(thing) == type(get_doc_for):
        nom = thing.__name__
        nom = string.replace(nom,'_','-')
        return """<a target="okbcdocs" href="%s">%s</a>""" % \
               (OKBC_SPEC_BASE_URL + nom,thing.__name__)
    return thing.__name__ or str(thing)
    

##########################################
#    Okbc methods
##########################################

from Funcs import *

##########################################
#    PrimorialKB
##########################################

Node._primordial_kb = AbstractPersistentKb('PRIMORDIAL_KB')
goto_kb(Node._primordial_kb)
PRIMORDIAL_KB = Node._primordial_kb

for f in primordials:
    Node._primordial_kb._add_frame_to_cache(f)
    
