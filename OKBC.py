
import exceptions

class OkbcCondition(exceptions.Exception):
    pass

class CardinalityViolation(OkbcCondition):
    def __init__(self,*args):
        self.args = args

class GenericError(OkbcCondition):
    pass

class Node:
    pass # so Symbol can subclass it

class Symbol(Node):
    name = None
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)

class Node:
    _all              = Symbol(':all')
    _template         = Symbol(':template')
    _own              = Symbol(':own')
    _slot_types       = (_all,_template,_own)
    _taxonomic        = Symbol(':taxonomic')
    _direct           = Symbol(':direct')
    _inference_levels = (_taxonomic,_all,_direct)
    _default_only     = Symbol(':default-only')
    _known_true       = Symbol(':known-true')
    _either           = Symbol(':either')
    _value_selectors  = (_either,_default_only,_known_true)
    _more             = Symbol(':more')
    _number_of_values = (_all,_more)
    _system_default   = Symbol(':system-default')
    _class            = Symbol(':class')
    _individual       = Symbol(':individual')
    _slot             = Symbol(':slot')
    _facet            = Symbol(':facet')
    _default          = Symbol(':default')

    def class_p(self):
        return None
    def connection_p(self):
        return None
    def facet_p(self):
        return None
    def individual_p(self):
        return None
    def kb_p(self):
        return None
    def procedure_p(self):
        return None
    def slot_p(self):
        return None




def class_p(thing):
    return thing.class_p()

def create_class(name,kb=None,kb_local_only_p=0):
    """Creates a class called name."""
    # p45
    if not kb: kb = current_kb()
    return kb.connection().create_frame_internal(name,KLASS,
                                                 kb,kb_local_only_p)

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
                      kb_local_only_p=0):
    """Creates an individual frame called name.
    Type direct types of the instance are given by direct-types.
    The other parameters have the same meaning as for create-frame."""
    # p45
    if not kb: kb = current_kb()
    return kb.create_frame_internal(name,Node._individual,
                                    kb=kb,
                                    direct_types=direct_types,
                                    own_slots = own_slots,
                                    own_facets = own_facets,
                                    handle = handle,
                                    pretty_name = pretty_name,
                                    kb_local_only_p=kb_local_only_p)

def create_slot(name,kb=None,kb_local_only_p=0):
    """Creates a slot called name."""
    # p45
    if not kb: kb = current_kb()
    return kb.connection().create_frame_internal(name,SLOT,
                                                  kb,kb_local_only_p)

def establish_connection(connection_type,initargs=None):
    return N3_CONNECTION(initargs)

def get_frame_in_kb(thing,kb=None,error_p=1,kb_local_only_p=0):
    """Returns a frame by name.
    Returns: (frame frame_in_kb_p)"""
    # p58
    if not kb: kb = current_kb()
    if not frame_in_kb_p(thing,kb,kb_local_only_p):
        return (0,0)
    else:
        return kb.get_frame_in_kb_internal(thing,kb,kb_local_only_p)

def get_frame_name(frame):
    # p58
    return frame.get_frame_name()

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
    # p58
    if not kb: kb = current_kb()
    if thing and isinstance(FRAME):
        return thing.get_frame_type(kb,inference_level,kb_local_only_p)
    else:
        return 0

def get_instance_types(frame, kb=None, inference_level=Node._taxonomic,
                       number_of_values = Node._all, kb_local_only_p = 0):
    # p59
    if not kb: kb = current_kb()
    if not inference_level == DIRECT:
        warn("inference_level " + str(inference_level) +
             "not supported, doing :direct")
    return get_slot_values(frame,"DIRECT-TYPE")

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

def get_kb_classes(kb=None,
                   selector=Node._system_default,
                   kb_local_only_p=0):
    # p60
    if not kb: kb = current_kb()
    return kb.get_kb_classes(kb,selector,kb_local_only_p)



class Connection:
    def __init__(initargs=None):
        pass

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
                              kb_local_only_p=1):
        if frame_type == Node._class:
            frame = CLASS(name,kb)
        elif frame_type == Node._individual:
            frame = INDIVIDUAL(name,kb)
        elif frame_type == Node._slot:
            frame = SLOT(name,kb)
        elif frame_type == Node._facet:
            frame = FACET(name,kb)
        else:
            raise GenericError()

        for dirtype in direct_types:
            frame.coerce_to_class(dirtype,kb=kb,
                                  kb_local_only_p=kb_local_only_p)

        for slot_spec in own_slots:
            slot = slot_spec[0]
            for slot_value_spec in slot_spec[-1:]:
                slot_values = []
                if (type(slot_value_spec) in [type([]),type(())]):
                    if slot_value_spec[0] == Node._default:
                        pass #save a default value slot_value_spec[1]
                    else:
                        pass # we are in a list but first elem != default
                else:
                    slot_values.append(slot_value_spec)
                frame.put_slot_values(slot,slot_values,
                                      kb_local_only_p=kb_local_only_p)

        return frame

##    def close_kb
##    def copy_kb
##    def create_kb
##    def create_kb_locator
##    def current_kb
##    def expunge_kb
##    def find_kb
##    def find_kb_locator
##    def find_kb_of_type
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


class META_KB(KB):
    def __init__(self,kb_name,
                 connection):
        # kb_name        the name of the new kb
        # connection     the connection for which this is the meta_kb
        connection.set_meta_kb(self)
        self._init_caches()
        self['connection'] = connection
        # self.fault_in()

    def get_kbs(self, connection=None):
        if not connection: connection = LOCAL_CONNECTION #FIXME
        return self.get_kb_type_instances('K') #FIXME

    
class MemoryKb(KB):
    def __init__(self):
        self._cache = {}

    def _add_frame_to_cache(self,frame):
        self._cache[frame.get_frame_name()] = frame


class FRAME(Node):
    def __init__(self,frame_name,kb=None):
        self._name = frame_name
        self._kb = kb
        self._direct_types = []
        self._frame_in_cache_p = 0
        if kb:
            kb._add_frame_to_cache(self)
        self._own_slots = {}
        self._template_slots = {}


    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self)

    def coerce_to_class(self,thing,
                        kb = None,
                        error_p = 1,
                        kb_local_only_p = 0):
        found_class = None
        class_found_p = thing.class_p() and thing.frame_in_kb_p(kb=kb)
        if class_found_p:
            if thing not in self._direct_types:
                self._direct_types.append(thing)
            found_class = thing
        elif error_p:
            raise ClassNotFound(thing,kb)            
        return (found_class,class_found_p)
        

    def get_frame_name(self):
        return self._name

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

    def get_slot_values(self,slot,
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
            if self._own_slots.has_key(slot):
                list_of_values.extend(self._own_slots[slot].values())
        if slot_type == [Node._template,Node._all]:
            if self._own_slots.has_key(slot):
                list_of_values.extend(self._own_slots[slot].values())
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
    def get_frame_type(self):
        return Node._class
    def _type_code(self):
        return "C"
    def class_p(self):
        return 1
    
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
    def facets(self):
        return self._facets
    def values(self):
        return self._values
    def set_value(self,value):
        self._values = [value]
    def set_values(self,values):
        self._values = values

class CLASS:
    pass

