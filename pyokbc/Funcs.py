
from PyOkbc import *
CURRENT_KB = None
LOCAL_CONNECTION = None

__allow_access_to_unprotected_subobjects__ = 1

def add_class_superclass(klass,new_superclass,
                         kb=None,kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.add_class_superclass(klass,new_superclass,kb_local_only_p)

def class_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()    
    return kb.class_p(thing,kb_local_only_p)

def connection(kb):
    return kb._connection

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
                                    doc = doc,
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

def find_kb(name_or_kb_or_kb_locator,connection = None):
    if not connection: connection = local_connection()
    return connection.find_kb(name_or_kb_or_kb_locator)

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
    # FIXME
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

def get_frame_sentences(frame, kb=None, number_of_values=Node._all,
                        okbc_sentences_p=1,value_selector=Node._either,
                        kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_sentences(frame,number_of_values,okbc_sentences_p,
                                  value_selector,kb_local_only_p)

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
    return kb.get_frame_type(thing,kb_local_only_p)

def get_instance_types(frame, kb=None, inference_level=Node._taxonomic,
                       number_of_values = Node._all, kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_instance_types(frame, inference_level,
                                 number_of_values, kb_local_only_p)

def get_kb_classes(kb=None,
                   selector = Node._system_default,
                   kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_classes(selector,kb_local_only_p)

def get_kb_direct_children(kb=None):
    if not kb: kb = current_kb()
    return kb.get_kb_direct_children()

def get_kb_direct_parents(kb=None):
    if not kb: kb = current_kb()
    return kb.get_kb_direct_parents()

def get_kb_facets(kb=None,
                  selector = Node._system_default,
                  kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_facets_internal(selector, kb_local_only_p)

def get_kb_frames(kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_kb_frames(kb_local_only_p)

def get_kb_individuals(kb=None,
                       selector = Node._system_default,
                       kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_individuals(selector,kb_local_only_p)

def get_kb_slots(kb=None,
                 selector = Node._system_default,
                 kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_slots_internal(selector,kb_local_only_p)

def get_slot_facets(frame,slot,kb=None,
                   inference_level = Node._taxonomic,
                   slot_type = Node._own,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_slot_facets(frame,slot,
                              inference_level,slot_type,
                              kb_local_only_p)

def get_slot_value(frame,slot,
                   kb=None,
                   inference_level = Node._taxonomic,
                   slot_type = Node._own,
                   value_selector = Node._either,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_slot_value(frame,slot,
                             inference_level,
                             slot_type,
                             value_selector,
                             kb_local_only_p)

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

def get_slot_values_in_detail(frame,slot,
                              kb=None,
                              inference_level = Node._taxonomic,
                              slot_type = Node._own,
                              number_of_values = Node._all,
                              value_selector = Node._either,
                              kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_slot_values_in_detail(frame,slot,
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

def instance_of_p(thing,klass,kb=None,                  
                  inference_level=Node._taxonomic,
                  kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.instance_of_p(thing,klass,inference_level,kb_local_only_p)

def kb_p(thing):
    return isinstance(thing,KB)

def local_connection():
    global LOCAL_CONNECTION
    if not LOCAL_CONNECTION:
        place = os.environ.get('LOCAL_CONNECTION_PLACE')
        #print "place =",place
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

def openable_kbs(kb_type=None,connection = None,place=None):
    if not connection: connection = local_connection()
    print "openable_kbs connection =",connection
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

def put_slot_value(frame,slot, value,
                   kb = None,
                   slot_type=Node._own,
                   value_selector = Node._known_true,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.put_slot_value(frame,slot,value,slot_type,
                             value_selector,kb_local_only_p)

def put_slot_values(frame,slot, values,
                    kb = None,
                    slot_type=Node._own,
                    value_selector = Node._known_true,
                    kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.put_slot_values(frame,slot,values,slot_type,
                              value_selector,kb_local_only_p)

def save_kb(kb=None,error_p=1):
    if not kb: kb = current_kb()
    return kb.save_kb(error_p=error_p)

def save_kb_as(new_name_or_locator,kb=None,error_p = 1):
    if not kb: kb = current_kb()
    kb.save_kb_as(new_name_or_locator,error_p=error_p)

def slot_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.slot_p(thing,kb_local_only_p)

def subclass_of_p(subclass,superclass,kb=None,
                  inference_level=Node._taxonomic,
                  kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.subclass_of_p(subclass,superclass,
                            inference_level,kb_local_only_p)

def superclass_of_p(superclass,subclass,kb=None,
                    inference_level=Node._taxonomic):
    if not kb: kb = current_kb()    
    return kb.subclass_of_p(superclass,subclass,
                            inference_level,kb_local_only_p)



##########################################
#   Methods outside of the OKBC spec
##########################################

def put_direct_parents(parent_kbs,kb=None):
    if not kb: kb = current_kb()
    kb.put_direct_parents(parent_kbs)
