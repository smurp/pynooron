
WARNINGS = 10
CURRENT_KB = None
LOCAL_CONNECTION = None

import exceptions
import copy



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
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)
    def docs(self):
        return "http://www.ai.sri.com/~okbc/spec/okbc2/okbc2.html#"+self.name
        

class Node:
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

    # facets
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


    def class_p(self):       return None
    def connection_p(self):  return None
    def facet_p(self):       return None
    def individual_p(self):  return None
    def kb_p(self):          return None
    def procedure_p(self):   return None
    def slot_p(self):        return None


class Connection:
    def __init__(connection,initargs=None):
        connection._meta_kb = META_KB('DefaultMetaKb',
                                      connection = connection)

    def retrieve_or_open(connection,kb_locator,kb_type,error_p):
        my_meta_kb = kb=connection._meta_kb
        (kb,frame_found_p) = get_frame_in_kb(kb_locator,
                                             kb = my_meta_kb,
                                             error_p=error_p)
        if not kb:
            new_kb = kb_type(kb_locator)
            my_meta_kb._add_frame_to_cache(new_kb)
            kb = new_kb
        return kb
##    def all_connections
##    def close_connection
##    def establish_connection
##    def local_connection

class CacheOnKb:
    """Caches keep track of a number of values and is capable of
    returning all the instances currently on the cache.  There
    is also a flag accessible via the accessor method _got_them_all()
    which records whether the cache is believed to hold all the
    items it ought to."""

class KB(Node):

    def kb_p(self):
        return 1
    
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

        kb.put_instance_types(frame,direct_types,
                              kb_local_only_p = kb_local_only_p)

        # FIXME should use mandatory put-class-superclasses
        for sclass in direct_superclasses:
            frame.add_class_superclass(sclass,
                                       kb = kb,
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
            frame.put_slot_values(slot,slot_values,
                                  kb_local_only_p=kb_local_only_p)
            #print "slot_values:",slot_values,"_slot_values:",frame._own_slots[slot]            


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
            #print "slot_values:",slot_values,"_slot_values:",frame._template_slots[slot]

        if doc: frame._doc = doc
        if pretty_name != None: frame._pretty_name = pretty_name
        
        return frame

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


    def get_kb_behaviours_internal(kb):
        return kb._behavior_values.keys()

    def get_behaviour_values_internal(kb,behavior):
        return kb._behavior_values.get(behavior,[])
        
    def get_frame_name(kb,frame,kb_local_only_p=0):
        if isinstance(kb,META_KB):
            return frame._name
        return frame.get_frame_name(kb_local_only_p=kb_local_only_p)

    def get_frame_pretty_name(kb,frame,kb_local_only_p=0):
        if isinstance(kb,META_KB):
            return frame._pretty_name
        return frame.get_frame_pretty_name(kb_local_only_p=kb_local_only_p)

    def get_frame_type_internal(kb,thing,kb_local_only_p=0):
        return thing.get_frame_type()

    def put_instance_types(kb,frame,new_types,
                           kb_local_only_p = 0):
        klop = kb_local_only_p
        new_direct_types = []
        orig_types = kb.get_instance_types(inference_level=Node._direct,
                                           kb_local_only_p = klop)
        for new_type in new_types:
            if kb.class_p(new_type):
                new_direct_types.append(new_type)
            else:
                resp = coerce_to_class(new_type,
                                       kb_local_only_p=klop)
                if resp[1]:
                    new_class = resp[0]
                    if not (new_class in orig_types):
                        new_direct_types.append(new_class)
        # this is so crude
        frame._direct_types = new_direct_types

    def coerce_to_class(kb,thing,error_p = 1,kb_local_only_p = 0):
        found_class = kb.create_frame(thing,Node._class)
        class_found_p = found_class
        if class_found_p:
            if thing not in thing._direct_types:
                self._direct_types.append()
        elif error_p:
            raise ClassNotFound(thing,kb)            
        return (found_class,class_found_p)


##    def close_kb
##    def copy_kb
##    def create_kb
##    def create_kb_locator
##    def current_kb
##    def expunge_kb
##    def find_kb
##    def find_kb_locator
##    def find_kb_of_type
##    def frame_in_kb_p
##    def generate_individual_name
##    def get_kb_direct_children
##    def get_kb_direct_parents
##    def get_kb_type
##    def get_kb_types
##    def get_kbs
##    def get_kbs_of_type
##    def goto_kb
##    def individual_name_generation_interactive_p
##    def kb_modified_p
##    def meta_kb
##    def open_kb
##    def openable_kbs
##    def revert_kb
##    def save_kb_as

#class TupleKb:
#    pass

class TupleKb(KB):
    def __init__(self):
        self._cache = {}
        self._typed_cache = {}
        for frame_type in Node._cache_types:
            self._typed_cache[frame_type] = []

    def _add_frame_to_cache(kb,frame):
        frame_name = kb.get_frame_name(frame)
        frame_type = get_frame_type(frame,kb=kb)
        kb._cache[frame_name] = frame
        kb._typed_cache[frame_type].append(frame)

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


class META_KB(TupleKb):
    def __init__(self,kb_name,
                 connection=None):
        # kb_name        the name of the new kb
        # connection     the connection for which this is the meta_kb
        meth = TupleKb.__init__
        meth(self)
        self._connection = connection


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

    def get_frame_pretty_name(frame,kb_local_only_p=0):
        return frame._pretty_name

    def get_instance_types(frame,
                           kb = None,
                           inference_level = Node._taxonomic,
                           number_of_values = Node._all,
                           kb_local_only_p = 0):
        warn("get_instance_types ignores kb_local_only_p",20)
        if inference_level in [Node._taxonomic,Node._all]:
            taxonomic_types = []
            for dclass in frame._direct_types:
                if not (dclass in taxonomic_types):
                    taxonomic_types.append(dclass)
                    taxonomic_types.extend(dclass.get_class_superclasses()[0])
            return (taxonomic_types,1,0)
        else:
            return (frame._direct_types,1,0)


    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self)

        
    def frame_in_kb_p(self,kb=None,kb_local_only_p=0):
        return kb.frame_in_kb_p_internal(self,kb_local_only_p=kb_local_only_p)

    def get_frame_name(frame,kb_local_only_p=0):
        return frame._name

    def get_frame_slots(self,
                        kb=None,
                        inference_level = Node._taxonomic,
                        slot_type = Node._all):
        retarray = []
        slot_name = ''
        if slot_type in [Node._all,Node._own]:
            for slot_name in self._own_slots.keys():
                retarray.append(slot_name)
        if slot_type in [Node._all,Node._template]:
            for slot_name in self._template_slots.keys():
                retarray.append(slot_name)
        return retarray

    def get_slot_values(frame,slot,
                        kb=None,
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
        list_of_values = []
        exact_p = 0
        if slot_type in [Node._own,Node._all]:
            if frame._own_slots.has_key(slot):
                list_of_values.extend(frame._own_slots[slot].values())
        if slot_type in [Node._template,Node._all]:
            if frame._template_slots.has_key(slot):
                list_of_values.extend(frame._template_slots[slot].values())
        return (list_of_values,exact_p,Node._all)

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
    def __init__(self,frame_name,kb=None):
        FRAME.__init__(self,frame_name,kb=kb)
        self._direct_super_classes = []        
    def get_frame_type(self):
        return Node._class
    def _type_code(self):
        return "C"
    def class_p(self):
        return 1

    def add_class_superclass(self,new_superclass,
                             kb=None,
                             kb_local_only_p = 0):
        
        if new_superclass not in self._direct_super_classes:
            self._direct_super_classes.append(new_superclass)
    
    def get_class_superclasses(self,
                               kb = None,
                               inference_level = Node._taxonomic,
                               number_of_values = Node._all,
                               kb_local_only_p = 0):
        if inference_level == Node._direct:
            return (copy.copy(self._direct_super_classes),1,0)
        supers = []
        self.get_superclasses_recurse(supers)
        return (supers,1,0)

    def get_superclasses_recurse(self,supers):
        for super in self._direct_super_classes:
            if not (super in supers):
                supers.append(super)
                super.get_superclasses_recurse(supers)
    
class INDIVIDUAL(FRAME):
    def get_frame_type(self):
        return Node._individual
    def _type_code(self):
        return "I"
    def individual_p(self):
        return 1
        
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
        dump_frame(frame)
        print ""

def dump_frame(frame):
    print frame.get_frame_name(),"("+str(get_frame_type(frame))+")"
    for klass in frame.get_instance_types(inference_level=Node._all)[0]:
        print "  Class:", klass
    if frame.class_p():
        for super in frame.get_class_superclasses()[0]:
            print "  Superclass:", super
    for slot in frame.get_frame_slots():
        print "  Slot:", slot
        print "     values: "+\
              str(frame.get_slot_values(slot,
                                        slot_type=Node._all)[0])
    print "own_slots:",frame._own_slots        
    print "template_slots:",frame._template_slots

    
def warn(mess,level=10):
    if WARNINGS >= level:
        print mess

##########################################
#    Okbc methods
##########################################


def class_p(thing):
    return thing.class_p()


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


def create_frame(name,frame_type,kb=None,kb_local_only_p=0):
    """Creates a class called name."""
    # p47
    if not kb: kb = current_kb()
    return kb.connection().create_frame_internal(name,frame_type,
                                                 kb,kb_local_only_p)

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
    return CURRENT_KB

def establish_connection(connection_type,initargs=None):
    return N3_CONNECTION(initargs)

def frame_in_kb_p(kb,thing,
                  kb_local_only_p = 0):
    if not kb: kb = current_kb()
    print "kb:",kb
    return kb.frame_in_kb_p_internal(thing,kb_local_only_p=kb_local_only_p)


def get_class_instances(klass,kb=None,inference_level=Node._taxonomic,
                        number_of_values = Node._all, kb_local_only_p=0):
    # p56
    """Returns: list-of-instances exact-p more=status"""
    if not kb: kb = current_kb()
    return kb.get_class_instances(klass,inference_level,
                                  number_of_values,kb_local_only_p)

def get_class_subclasses(klass, kb=None, inference_level=Node._taxonomic,
                         number_of_values=Node._all, kb_local_only_p=0):
    return kb.get_class_subclasses(inference_level,number_of_values,
                                   kb_local_only_p)

def get_class_superclasses(klass, kb=None, inference_level=Node._taxonomic,
                           number_of_values=Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    if not inference_level == DIRECT:
        warn("inference_level " + str(inference_level) +
             "not supported, doing :direct")
    return get_slot_values(klass,"DIRECT-SUPER")

def get_frame_in_kb(thing,kb=None,error_p=1,kb_local_only_p=0):
    """Returns a frame by name.
    Returns: (frame frame_in_kb_p)"""
    # p58
    if not kb: kb = current_kb()
    if not kb.frame_in_kb_p(thing,kb_local_only_p):
        return (0,0)
    else:
        return kb.get_frame_in_kb_internal(thing,kb_local_only_p)

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
    return frame.get_frame_slots(kb,inference_level,slot_type,
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
    if not inference_level == DIRECT:
        warn("inference_level " + str(inference_level) +
             "not supported, doing :direct")
    die("not implemented")
    return get_slot_values(frame,"DIRECT-TYPE")

def get_kb_classes(kb=None,
                   selector = Node._system_default,
                   kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_classes_internal(selector = selector,
                                      kb_local_only_p=kb_local_only_p)

def get_kb_facets(kb=None,
                  selector = Node._system_default,
                  kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_facets_internal(selector = selector,
                                     kb_local_only_p = kb_local_only_p)

def get_kb_frames(kb=None,kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_frames_internal(kb_local_only_p=kb_local_only_p)

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
    return kb.get_kb_slots_internal(selector = selector,
                                    kb_local_only_p = kb_local_only_p)

def goto_kb(kb):
    global CURRENT_KB
    CURRENT_KB = kb

def local_connection():
    global LOCAL_CONNECTION
    if not LOCAL_CONNECTION: LOCAL_CONNECTION = Connection()
    return LOCAL_CONNECTION

def open_kb(kb_locator,
            kb_type = None,
            connection = None,
            error_p = 1):
    if not connection: connection = local_connection()
    if not kb_type:
        from OkbcPythonKb import OkbcPythonKb
        kb_type = OkbcPythonKb
    return connection.retrieve_or_open(kb_locator,kb_type,error_p)

            
def save_kb(kb=None,error_p=1):
    if not kb: kb = current_kb()
    return kb.save_kb(error_p=error_p)
