
WARNINGS = 2
# 10 critical
# 20 noops
# 30 subtleties
CURRENT_KB = None
LOCAL_CONNECTION = None
PRIMORDIAL_KB = ()

import exceptions
import copy
import os

##########################################
#    Classes
##########################################    

class OkbcCondition(exceptions.Exception):
    pass

class CardinalityViolation(OkbcCondition):
    def __init__(self,*args):
        self.args = args

class ClassNotFound(OkbcCondition):    pass
class GenericError(OkbcCondition):     pass

class Node:
    pass # so Symbol can subclass it

class Symbol(Node):
    def __init__(self,name):
        self._name = name
    def __str__(self):
        try:
            return self._name
        except:
            return 'unknown'
    def __repr__(self):
        return str(self)
    def _docs(self):
        return "http://www.ai.sri.com/~okbc/spec/okbc2/okbc2.html#"+self.name

class Node(Symbol):
    _all                      = Symbol(':all')
    _own                      = Symbol(':own')
    _template                 = Symbol(':template')
    _slot_types               = (_all,_template,_own)
    
    _taxonomic                = Symbol(':taxonomic')
    _direct                   = Symbol(':direct')
    _inference_levels         = (_taxonomic,_all,_direct)
    
    _default_only             = Symbol(':default-only')
    _known_true               = Symbol(':known-true')
    _either                   = Symbol(':either')
    _value_selectors          = (_either,_default_only,_known_true)
    
    _more                     = Symbol(':more')
    _number_of_values         = (_all,_more)
    
    _class                    = Symbol(':class')
    _individual               = Symbol(':individual')
    _slot                     = Symbol(':slot')
    _facet                    = Symbol(':facet')
    _kb                       = Symbol(':kb') # not included in _frame_types
    _frame_types              = (_class,_individual,_slot,_facet)
    _cache_types              = _frame_types + (_kb,)
    
    _value                    = Symbol(':value')
    _frame                    = Symbol(':frame')
    _target_contexts          = (_frame,_slot,_facet,_class,_individual,_value)
    
    _system_default           = Symbol(':system-default')
    _frames                   = Symbol(':frames')
    _selector_all             = (_all,_frames,_system_default)
    _default                  = Symbol(':default')

    _filled                   = Symbol(':filled')

    # initargs
    _port                     = Symbol(':port')
    _host                     = Symbol(':host')
    _password                 = Symbol(':password')
    _username                 = Symbol(':username')
    _parent_kbs               = Symbol(':parent-kbs')

    # facets (redefined later using create_facet)
    _VALUE_TYPE               = Symbol(':VALUE-TYPE')
    _INVERSE                  = Symbol(':INVERSE')
    _CARDINALITY              = Symbol(':CARDINALITY')
    _MAXIMUM_CARDINALITY      = Symbol(':MAXIMUM-CARDINALITY')
    _MINIMUM_CARDINALITY      = Symbol(':MINIMUM-CARDINALITY')
    _SAME_VALUES              = Symbol(':SAME-VALUES')
    _NOT_SAME_VALUES          = Symbol(':NOT-SAME-VALUES')
    _SUBSET_OF_VALUES         = Symbol(':SUBSET-OF-VALUES')
    _NUMERIC_MINIMUM          = Symbol(':NUMERIC-MINIMUM')
    _NUMERIC_MAXIMUM          = Symbol(':NUMERIC-MAXIMUM')
    _SOME_VALUES              = Symbol(':SOME-VALUES')
    _COLLECTION_TYPE          = Symbol(':COLLECTION-TYPE')
    _DOCUMENTATION_IN_FRAME   = Symbol(':DOCUMENTATION-IN-FRAME')
    


    # behavior values
    _never                    = Symbol(':never')
    _immediate                = Symbol(':immediate')
    _user_defined_facets      = Symbol(':user-defined-facets')
    _facets_reported          = Symbol(':facets-reported')    
    _read_only                = Symbol(':read-only')
    _monotonic                = Symbol(':monotonic')
    _deferred                 = Symbol(':deferred')
    _background               = Symbol(':background')
    _override                 = Symbol(':override')
    _when_consistent          = Symbol(':when-consistent')
    _none                     = Symbol(':none')
    _list                     = Symbol(':list')
    
    # behaviors
    _are_frames               = Symbol(':are-frames')
    _are_frames_all           = (_class,_individual,_slot,_facet)
    _class_slot_types         = Symbol(':class-slot-types')
    _class_slot_types_all     = (_template, _own)
    _collection_types         = Symbol(':collection-types')
    _compliance               = Symbol(':compliance')
    _compliance_all             = (_facets_reported,
                                   _user_defined_facets,
                                   _read_only,
                                   _monotonic)
    _constraints_checked      = Symbol(':constraints-checked')
    _constraints_checked_all  = (_VALUE_TYPE,
                                 _INVERSE,
                                 _CARDINALITY,
                                 _MAXIMUM_CARDINALITY,
                                 _MINIMUM_CARDINALITY,
                                 _SAME_VALUES,
                                 _NOT_SAME_VALUES,
                                 _SUBSET_OF_VALUES,
                                 _NUMERIC_MINIMUM,
                                 _NUMERIC_MAXIMUM,
                                 _SOME_VALUES,
                                 _COLLECTION_TYPE,
                                 _DOCUMENTATION_IN_FRAME)
    _constraint_checking_time = Symbol(':constraint-time-checking')
    _constraint_checking_time_all = (_immediate,_deferred,_background,_never)
    _constraint_report_time   = Symbol(':constraint-report-time')
    _constraint_report_time_all = (_immediate,_deferred)
    _defaults                 = Symbol(':defaults')
    _defaults_all             = (_override,
                                 _when_consistent,
                                 _none)

    _behaviours_all           = (_are_frames,
                                 _class_slot_types,
                                 _collection_types,
                                 _compliance,
                                 _constraints_checked,
                                 _constraint_checking_time,
                                 _constraint_report_time,
                                 _defaults)

class FRAME(Node):
    def __init__(self,frame_name,kb=None):
        self._name = frame_name
        self._kb = kb
        self._direct_types = []
        self._frame_in_cache_p = 0
        self._pretty_name = None
        if kb:
            kb._add_frame_to_cache(self)
        self._own_slots = {}
        self._template_slots = {}
        self._doc = None

    def __str__(self):
        #return "<"+self._name+">"
        return self._name

    def __repr__(self):
        return str(self)

    def frame_in_kb_p(self,kb=None,kb_local_only_p=0):
        return kb.frame_in_kb_p_internal(self,kb_local_only_p)

    def get_frame_name(frame,kb_local_only_p=0):
        return frame._name

    def put_slot_value(self,slot, value,
                       kb=None,
                       slot_type=Node._own,
                       value_selector = Node._known_true,
                       kb_local_only_p = 0):
        """Sets the values of slot in frame to be a singleton set
        consisting of a single element: value.  This operation may
        signal constraint violation conditions (see Section 3.8).
        Returns no values. """
        if type(value) == type([]): raise CardinalityViolation(value)
        if slot_type == Node._own:
            if self._own_slots.has_key(slot):
                self._own_slots[slot].set_value(value)
            else:
                self._own_slots[slot] = UNIT_SLOT(slot,value)
        elif slot_type == Node._template:
            if self._template_slots.has_key(slot):
                self._template_slots[slot].set_value(value)
            else:
                self._template_slots[slot] = UNIT_SLOT(slot,value)

    def put_slot_values(self,slot, values,
                        kb=None,
                        slot_type=Node._own,
                        value_selector = Node._known_true,
                        kb_local_only_p = 0):
        """Sets the values of slot in frame to be a singleton set
        consisting of a single element: value.  This operation may
        signal constraint violation conditions (see Section 3.8).
        Returns no values. """
        if type(values) != type([]): raise CardinalityViolation(values)
        if slot_type == Node._own:
            if self._own_slots.has_key(slot):
                self._own_slots[slot].set_values(values)
            else:
                self._own_slots[slot] = UNIT_SLOT(slot,values)
        elif slot_type == Node._template:
            if self._own_slots.has_key(slot):
                self._template_slots[slot].set_values(values)
            else:
                self._template_slots[slot] = UNIT_SLOT(slot,values)

class KLASS(FRAME):
    def __init__(klass,frame_name,kb=None):
        FRAME.__init__(klass,frame_name,kb=kb)
        klass._direct_superclasses = []        
    def get_frame_type(klass):
        return Node._class
    def _type_code(klass):
        return "C"
#    def class_p(klass):
#        return 1

    def add_class_superclass(klass,new_superclass,
                             kb=None,
                             kb_local_only_p = 0):
        if new_superclass not in klass._direct_superclasses:
            klass._direct_superclasses.append(new_superclass)
    
    
class INDIVIDUAL(FRAME):
    def get_frame_type(self):
        return Node._individual
    def _type_code(self):
        return "I"
#    def individual_p(self):
#        return 1
        
class SLOT(FRAME):
    def get_frame_type(self):
        return Node._slot
    def _type_code(self):
        return "S"
    def slot_p(self):
        return 1

class FACET(FRAME):
    def get_frame_type(self):
        return Node._facet
    def _type_code(self):
        return "F"
    def facet_p(self):
        return 1


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
        
        kb = kb_type(kb_locator,initargs=initargs)
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
            kb = kb_type(kb_locator)
            my_meta_kb._add_frame_to_cache(kb)
        return kb

    def openable_kbs(connection, kb_type = None, place = None):
        warn("openable_kbs is a noop",20)
        return []
    
##    def all_connections
##    def close_connection
##    def establish_connection
##    def local_connection


class KB(Node):
    """All OKBC methods which take a KB argument should be implemented here.
    The exceptions are the mandatory ones.  All of them are implemented in
    TupleKB.  That leaves all optional methods, which should be implemented
    here.  Oh I am sure this is all screwed up!"""
    def __init__(kb,name,initargs = {}):
        kb._name = name        
        kb._initargs = initargs
        parent_kbs = initargs.get(Node._parent_kbs,[])
        if PRIMORDIAL_KB:
            parent_kbs.append(PRIMORDIAL_KB)
        kb._parent_kbs = parent_kbs
    
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
            raise ClassNotFound(thing,kb)
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
                frame = KLASS(name,kb)
            elif frame_type == Node._individual:
                frame = INDIVIDUAL(name,kb)
            elif frame_type == Node._slot:
                frame = SLOT(name,kb)
            elif frame_type == Node._facet:
                frame = FACET(name,kb)
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
            frame.put_slot_values(slot,slot_values,
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
            frame.put_slot_values(slot,slot_values,
                                  slot_type=Node._template,
                                  kb_local_only_p=kb_local_only_p)

        if doc: frame._doc = doc
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
        if isinstance(kb,KB):
            return frame._name
        return frame.get_frame_name(kb_local_only_p=kb_local_only_p)
    get_frame_name = get_frame_name_internal

    def get_frame_pretty_name_internal(kb,frame,kb_local_only_p=0):
        #if isinstance(kb,META_KB):
        #    return frame._pretty_name
        return frame._pretty_name
    get_frame_pretty_name = get_frame_pretty_name_internal

    def get_frame_slots(kb,frame,
                        inference_level = Node._taxonomic,
                        slot_type = Node._all,
                        kb_local_only_p = 0):
        klop = kb_local_only_p
        il = inference_level
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
        if inference_level in [Node._taxonomic,Node._all]:
            taxonomic_types = []
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
            warn(str(frame)+" missing "+str(slot))
            raise
        (list_of_values,
         exact_p,
         more_status) = kb.get_slot_values_internal(found_frame,
                                                    found_slot,
                                                    inference_level,
                                                    slot_type,
                                                    number_of_values,
                                                    value_selector,
                                                    kb_local_only_p)
        if inference_level in [Node._taxonomic,Node._all] and \
           slot_type != Node._own:
            for klass in kb.get_instance_types(frame,
                                               inference_level=il)[0]:
                #print "===>",klass,klass._template_slots
                for val in kb.get_slot_values(klass,slot,
                                              inference_level=inference_level,
                                              slot_type=Node._template)[0]:
                    #print "  =>",val
                    if not (val in list_of_values):
                        list_of_values.append(val)

        return (list_of_values,exact_p,more_status)

    def individual_p(kb,thing,kb_local_only_p = 0):
        return isinstance(thing,INDIVIDUAL)

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
    def __init__(self,name=''):
        KB.__init__(self,name)
        self._cache = {}
        self._typed_cache = {}
        for frame_type in Node._cache_types:
            self._typed_cache[frame_type] = []

    def _add_frame_to_cache(kb,frame):
        frame_name = kb.get_frame_name(frame)
        frame_type = get_frame_type(frame,kb=kb)
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

    def class_p(kb,thing,kb_local_only_p = 0):
        return isinstance(thing,KLASS)

    def subclass_of_p(kb,subclass,superclass,
                      inference_level=Node._taxonomic,
                      kb_local_only_p = 0):
        #print "is",subclass,"a subclass of",superclass,"?",
        return kb.superclass_of_p(superclass,subclass,inference_level)

    def superclass_of_p(kb,superclass,subclass,
                        inference_level=Node._taxonomic):
        supers = kb.get_class_superclasses(subclass,inference_level)
        #print supers
        if superclass in supers[0]:
            #print "yes"
            return 1
        else:
            #print "no"
            return 0

    def get_class_subclasses_internal(kb,klass,
                                      inference_level = Node._taxonomic,
                                      number_of_values = Node._all,
                                      kb_local_only_p = 0):
        subclasses = []
        #print kb._name,kb._typed_cache
        for a_class in kb._typed_cache[Node._class]:
            if kb.subclass_of_p(a_class,klass,inference_level,kb_local_only_p):
                subclasses.append(a_class)
                #print a_class,"is a subclass of",klass
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
            for slot_name in frame._own_slots.keys():
                retarray.append(slot_name)
        if slot_type in [Node._all,Node._template]:
            for slot_name in frame._template_slots.keys():
                retarray.append(slot_name)
        return (retarray,1)

    def get_frame_type(kb,thing,kb_local_only_p=0):
        if thing:
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


class META_KB(TupleKb):
    def __init__(self,kb_name,
                 connection=None):
        # kb_name        the name of the new kb
        # connection     the connection for which this is the meta_kb
        meth = TupleKb.__init__
        meth(self,kb_name)
        self._connection = connection


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

##########################################
#    Okbc methods
##########################################


def class_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()    
    return kb.class_p(thing,kb_local_only_p)

def connection_p(thing):
    return isinstance(thing,Connection)

def create_class(name,kb=None,
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
    """Creates a class called name."""
    if not kb: kb = current_kb()
    return kb.create_frame_internal(name,Node._class,
                                    direct_types=direct_types,
                                    direct_superclasses=direct_superclasses,
                                    primitive_p=primitive_p,
                                    doc=doc,
                                    template_slots = template_slots,
                                    template_facets = template_facets,
                                    own_slots = own_slots,
                                    own_facets = own_facets,
                                    handle = handle,
                                    pretty_name = pretty_name,
                                    kb_local_only_p = kb_local_only_p
                                    )

def create_facet(name,
                 kb=None,
                 frame_or_nil = None,
                 slot_or_nil = None,
                 slot_type = Node._own,
                 direct_types = [],
                 doc = None,
                 own_slots = [],
                 own_facets = [],
                 handle = None,
                 pretty_name = None,
                 kb_local_only_p = 0):
    if not kb: kb = current_kb()
    warn("create_facet should call create_facet_internal",20)
    return kb.create_frame_internal(name,Node._facet,
                                    direct_types = direct_types,
                                    own_slots = own_slots,
                                    own_facets = own_facets,
                                    handle = handle,
                                    pretty_name = pretty_name,
                                    kb_local_only_p = kb_local_only_p)
    
def create_individual(name,
                      kb=None,
                      direct_types = [],
                      doc = None,
                      own_slots = [],
                      own_facets = [],
                      handle = None,
                      pretty_name = None,
                      kb_local_only_p = 0):
    """Creates an individual frame called name.
    Type direct types of the instance are given by direct-types.
    The other parameters have the same meaning as for create-frame."""
    # p45
    if not kb: kb = current_kb()
    return kb.create_frame_internal(name,Node._individual,
                                    direct_types = direct_types,
                                    own_slots = own_slots,
                                    own_facets = own_facets,
                                    handle = handle,
                                    pretty_name = pretty_name,
                                    kb_local_only_p = kb_local_only_p)

def create_kb(name,kb_type=None,kb_locator=None,initargs={},connection=None):
    if not connection: connection = local_connection()
    return connection.create_kb(kb_type,kb_locator,initargs)

def create_slot(name,
                kb=None,
                frame_or_nil = None,
                slot_type = Node._all,
                direct_types = [],
                doc = None,
                own_slots = [],
                own_facets = [],
                handle = None,
                pretty_name = None,
                kb_local_only_p = 0):
    """Creates a slot called name."""
    # p45
    if not kb: kb = current_kb()
    return kb.create_slot_internal(name,
                                   frame_or_nil = frame_or_nil,
                                   slot_type = slot_type,
                                   direct_types = direct_types,
                                   doc = doc,
                                   own_slots = own_slots,
                                   own_facets = own_facets,
                                   handle = handle,
                                   pretty_name = pretty_name,
                                   kb_local_only_p = kb_local_only_p)

def current_kb():
    global CURRENT_KB
    if not CURRENT_KB: CURRENT_KB = meta_kb()
    return CURRENT_KB

def establish_connection(connection_type,initargs=None):
    return connection_type(initargs)

def frame_in_kb_p(kb,thing, kb_local_only_p = 0):
    if not kb: kb = current_kb()
    print "kb:",kb
    return kb.frame_in_kb_p_internal(thing,kb_local_only_p)

def get_class_instances(klass,kb=None,inference_level=Node._taxonomic,
                        number_of_values = Node._all, kb_local_only_p=0):
    """Returns: list-of-instances exact-p more=status"""
    if not kb: kb = current_kb()
    return kb.get_class_instances(klass,inference_level,
                                  number_of_values,kb_local_only_p)

def get_class_subclasses(klass, kb=None, inference_level=Node._taxonomic,
                         number_of_values=Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_class_subclasses(klass,inference_level,number_of_values,
                                   kb_local_only_p)

def get_class_superclasses(klass, kb=None, inference_level=Node._taxonomic,
                           number_of_values=Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_class_superclasses(klass,
                                     inference_level=inference_level,
                                     number_of_values=number_of_values,
                                     kb_local_only_p=kb_local_only_p)

def get_frame_in_kb(thing,kb=None,error_p=1,kb_local_only_p=0):
    """Returns a frame by name.
    Returns: (frame frame_in_kb_p)"""
    # p58
    if not kb: kb = current_kb()
    if not kb.frame_in_kb_p(thing,kb_local_only_p):
        return (0,0)
    else:
        return kb.get_frame_in_kb(thing,kb_local_only_p)

def get_frame_name(frame,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_name(frame,kb_local_only_p=kb_local_only_p)

def get_frame_pretty_name(frame,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_pretty_name(frame,kb_local_only_p=kb_local_only_p)

def get_frame_slots(frame, kb=None, inference_level=Node._taxonomic,
                    slot_type=Node._all, kb_local_only_p=0):
    """Returns list-of-slots, a list of all the own, template, or own
    and template slots that are associated with frame, depending on the
    value of slot-type."""
    # p58
    if not kb: kb = current_kb()
    return kb.get_frame_slots(frame,inference_level,slot_type,
                              kb_local_only_p)

def get_frame_type(thing, kb=None, inference_level=Node._taxonomic,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_frame_type(thing,kb_local_only_p=kb_local_only_p)
    if thing:
        if isinstance(thing,KB):
            return Node._kb  # FIXME
        elif isinstance(thing,FRAME):
            return kb.get_frame_type(kb_local_only_p=kb_local_only_p)
    else:
        return 0

def get_instance_types(frame, kb=None, inference_level=Node._taxonomic,
                       number_of_values = Node._all, kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_instance_types(frame,inference_level=inference_level,
                                 number_of_values=number_of_values,
                                 kb_local_only_p=kb_local_only_p)

def get_kb_classes(kb=None,
                   selector = Node._system_default,
                   kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_classes(selector,kb_local_only_p)

def get_kb_direct_parents(kb=None):
    if not kb: kb = current_kb()
    return kb.get_kb_direct_parents()

def get_kb_facets(kb=None,
                  selector = Node._system_default,
                  kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_facets_internal(selector = selector,
                                     kb_local_only_p = kb_local_only_p)

def get_kb_frames(kb=None,kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_frames(kb_local_only_p)

def get_kb_individuals(kb=None,
                       selector = Node._system_default,
                       kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_individuals_internal(selector = selector,
                                          kb_local_only_p = kb_local_only_p)

def get_kb_slots(kb=None,
                 selector = Node._system_default,
                 kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_slots_internal(selector,kb_local_only_p)

def get_slot_values(frame,slot,
                    kb=None,
                    inference_level = Node._taxonomic,
                    slot_type = Node._own,
                    number_of_values = Node._all,
                    value_selector = Node._either,
                    kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_slot_values(frame,slot,
                              inference_level,
                              slot_type,
                              number_of_values,
                              value_selector,
                              kb_local_only_p)


def goto_kb(kb):
    global CURRENT_KB
    CURRENT_KB = kb

def individual_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.individual_p(thing,kb_local_only_p)

def kb_p(thing):
    return isinstance(thing,KB)

def local_connection():
    global LOCAL_CONNECTION
    if not LOCAL_CONNECTION:
        place = os.environ.get('LOCAL_CONNECTION_PLACE')
        if place != None:
            from FileSystemConnection import FileSystemConnection
            LOCAL_CONNECTION = FileSystemConnection({'default_place':place})
        else:
            LOCAL_CONNECTION = Connection()
    return LOCAL_CONNECTION

def meta_kb(connection = None):
    if not connection: connection = local_connection()
    return connection.meta_kb()

def open_kb(kb_locator,
            kb_type = None,
            connection = None,
            error_p = 1):
    if not connection: connection = local_connection()
    return connection.open_kb(kb_locator,kb_type,error_p)

def openable_kbs(kb_type,connection = None,place=None):
    if not connection: connection = local_connection()
    return connection.openable_kbs(kb_type,place)

def print_frame(frame,
                kb = None,
                slots = Node._filled,
                facets = Node._filled,
                stream = 1,
                inference_level = Node._taxonomic,
                number_of_values = Node._all,
                value_selector = Node._either,
                kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.print_frame(frame,slots,facets,stream,inference_level,
                          number_of_values,value_selector,kb_local_only_p)
    return kb.print_frame(frame,
                          slots = slots,
                          facets = facets,
                          stream = stream,
                          inference_level = inference_level,
                          number_of_values = number_of_values,
                          value_selector = value_selector,
                          kb_local_only_p = kb_local_only_p)

def procedure_p(thing):
    return isinstance(thing,PROCEDURE)

def put_class_superclasses(klass,new_superclasses,kb=0,kb_local_only_p=0):
    if not kb: kb = current_kb()
    kb.put_class_superclasses(klass,new_superclasses,kb_local_only_p)

def put_instance_types(frame,new_types,kb=0,kb_local_only_p = 0):
    if not kb: kb = current_kb()
    kb.put_instance_types(frame,new_types,kb_local_only_p)

def save_kb(kb=None,error_p=1):
    if not kb: kb = current_kb()
    return kb.save_kb(error_p=error_p)

def save_kb_as(new_name_or_locator,kb=None,error_p = 1):
    if not kb: kb = current_kb()
    kb.save_kb_as(new_name_or_locator,error_p=error_p)

def slot_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.slot_p(thing,kb_local_only_p)

##########################################
#   Methods outside of the OKBC spec
##########################################

def put_direct_parents(parent_kbs,kb=None):
    if not kb: kb = current_kb()
    kb.put_direct_parents(parent_kbs)

##########################################
#    PrimorialKB
##########################################

Node._primordial_kb = AbstractPersistentKb('PRIMORDIAL_KB')
goto_kb(Node._primordial_kb)
PRIMORDIAL_KB = Node._primordial_kb

    # Standard Classes
Node._THING = create_class(":THING",
             direct_types=[':CLASS'],
             doc=""":THING is the root of the class hierarchy for a KB, meaning
             that :THING is the superclass of every class in every KB.""")
Node._CLASS = create_class(":CLASS",
             direct_types=[':CLASS'],
             doc=""":CLASS is the class of all classes. That is, every entity
             that is a class is an instance of :CLASS.""")
Node._INDIVIDUAL = create_class(":INDIVIDUAL",
             direct_types=[':CLASS'],
             doc=""":INDIVIDUAL is the class of all entities that are not
             classes. That is, every entity that is not a class is an
             instance of :INDIVIDUAL.""")
Node._NUMBER = create_class(":NUMBER",
             direct_types=[':CLASS'],
             direct_superclasses=[':INDIVIDUAL'],
             doc=""":NUMBER is the class of all numbers.
             OKBC makes no guarantees about the precision of numbers.
             If precision is an issue for an application, then the
             application is responsible for maintaining and validating
             the format of numerical values of slots and facets.
             :NUMBER is a subclass of :INDIVIDUAL.""")
Node._INTEGER = create_class(":INTEGER",
             direct_types=[':CLASS'],
             direct_superclasses=[':NUMBER'],
             doc=""":INTEGER is the class of all integers and is a
             subclass of :NUMBER. As with numbers in general, OKBC makes
             no guarantees about the precision of integers.""")
Node._STRING = create_class(":STRING",
             direct_types=[':CLASS'],
             direct_superclasses=[':INDIVIDUAL'],
             doc=""":STRING is the class of all text strings.
             :STRING is a subclass of :INDIVIDUAL. """)
Node._SEXPR = create_class(":SEXPR",
             direct_types=[':CLASS'],
             doc=""":SEXP is not documented in OKBC v2.03""")
Node._SYMBOL = create_class(":SYMBOL",
             direct_types=[':CLASS'],
             direct_superclasses=[':SEXPR'],       
             doc=""":SYMBOL is the class of all symbols.
             :SYMBOL is a subclass of :SEXPR.""")
Node._LIST =  create_class(":LIST",
             direct_types=[':CLASS'],
             direct_superclasses=[':INDIVIDUAL'],
             doc=""":LIST is the class of all lists. 
             :LIST is a subclass of :INDIVIDUAL. """)

    # standard facets
Node._VALUE_TYPE =  create_facet(":VALUE-TYPE")
Node._INVERSE = create_facet(":INVERSE")
Node._CARDINALITY =  create_facet(":CARDINALITY")
Node._VALUE_TYPE =  create_facet(":VALUE-TYPE")
Node._MAXIMUM_CARDINALITY =  create_facet(":MAXIMUM-CARDINALITY")
Node._MINIMUM_CARDINALITY =  create_facet(":MINIMUM-CARDINALITY")
Node._SAME_VALUES = create_facet(":SAME-VALUES")
Node._NOT_SAME_VALUES = create_facet(":NOT-SAME-VALUES")
Node._SUBSET_OF_VALUES = create_facet(":SUBSET-OF-VALUES")
Node._NUMERIC_MINIMUM = create_facet(":NUMERIC-MINIMUM")
Node._NUMERIC_MAXIMUM = create_facet(":SAME-VALUES")
Node._SOME_VALUES = create_facet(":SOME-VALUES")
Node._COLLECTION_TYPE = create_facet(":COLLECTION-TYPE")
Node._DOCUMENTATION_IN_FRAME = create_facet(":DOCUMENTATION-IN-FRAME")

    # Slots on slot frames okbc2.html#3169
Node._DOMAIN = create_slot(":DOMAIN")
Node._SLOT_VALUE_TYPE = create_slot(":SLOT-VALUE-TYPE")
Node._SLOT_INVERSE = create_slot(":SLOT-INVERSE")
Node._SLOT_CARDINALITY = create_slot(":SLOT-CARDINALITY")
Node._SLOT_MAXIMUM_CARDINALITY = create_slot(":SLOT-MAXIMUM-CARDINALITY")
Node._SLOT_MINIMUM_CARDINALITY = create_slot(":SLOT-MINIMUM-CARDINALITY")
Node._SLOT_SAME_VALUES = create_slot(":SLOT-SAME-VALUES")
Node._SLOT_NOT_SAME_VALUES = create_slot(":SLOT-NOT-SAME-VALUES")
Node._SLOT_SUBSET_OF_VALUES = create_slot(":SLOT-SUBSET-OF-VALUES")
Node._SLOT_NUMERIC_MINIMUM = create_slot(":SLOT-NUMERIC-MINIMUM")
Node._SLOT_NUMERIC_MAXIMUM = create_slot(":SLOT-NUMERIC-MAXIMUM")
Node._SLOT_SOME_VALUES = create_slot(":SLOT-SOME-VALUES")
Node._SLOT_COLLECTION_TYPE = create_slot(":SLOT-COLLECTION-TYPE")
