
from PyOkbc import *
CURRENT_KB = None
LOCAL_CONNECTION = None

__allow_access_to_unprotected_subobjects__ = 1

def add_class_superclass(klass,new_superclass,
                         kb=None,kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.add_class_superclass(klass,new_superclass,kb_local_only_p)
add_class_superclass.enumerator=0
add_class_superclass.optional=1
add_class_superclass.read=0
add_class_superclass.mandatory=0
add_class_superclass.write=1

# def add_facet_value
# def add_instance_type
# def add_slot_value
# def all_connections
# def allocate_frame_handle
# def ask
# def askable
# def attach_facet
# def attach_slot

def call_procedure(procedure,kb=None,arguments=None):
    if not kb: kb = current_kb()
    return kb.call_procedure(procedure,arguments)
call_procedure.enumerator=1
call_procedure.optional=1
call_procedure.read=1
call_procedure.mandatory=0
call_procedure.write=0


def class_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()    
    return kb.class_p(thing,kb_local_only_p)
class_p.enumerator=0
class_p.optional=0
class_p.read=1
class_p.mandatory=1
class_p.write=0


# def close_connection
# def close_kb

def connection(kb): # FIXME not in OKBC Spec
    return kb._connection

# def coerce_to_class
# def coerce_to_facet
# def coerce_to_frame
# def coerce_to_individual
# def coerce_to_kb_value
# def coerce_to_slot
# def coercible_to_frame_p

def connection_p(thing):
    return isinstance(thing,Connection)
connection_p.enumerator=0
connection_p.optional=0
connection_p.read=1
connection_p.mandatory=0
connection_p.write=0

# def continuable_error_p
# def copy_frame
# def copy_kb

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
create_class.enumerator=1
create_class.optional=1
create_class.read=1
create_class.mandatory=0
create_class.write=0

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
    return kb.create_frame_internal(name,Node._facet,
                                    direct_types = direct_types,
                                    own_slots = own_slots,
                                    own_facets = own_facets,
                                    handle = handle,
                                    pretty_name = pretty_name,
                                    kb_local_only_p = kb_local_only_p)
create_facet.enumerator=0
create_facet.optional=0
create_facet.read=0
create_facet.mandatory=1
create_facet.write=1

# def create_frame

def create_individual(name,
                      kb=None,
                      direct_types = [],
                      doc = None,
                      own_slots = [],
                      own_facets = [],
                      handle = None,
                      pretty_name = None,
                      kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.create_frame_internal(name,Node._individual,
                                    direct_types = direct_types,
                                    doc = doc,
                                    own_slots = own_slots,
                                    own_facets = own_facets,
                                    handle = handle,
                                    pretty_name = pretty_name,
                                    kb_local_only_p = kb_local_only_p)
create_individual.enumerator=0
create_individual.optional=1
create_individual.read=0
create_individual.mandatory=0
create_individual.write=1

def create_kb(name,kb_type=None,kb_locator=None,
              initargs={},connection=None):
    if not connection: connection = local_connection()
    return connection.create_kb(kb_type,kb_locator,initargs)
create_kb.enumerator=0
create_kb.optional=1
create_kb.read=0
create_kb.mandatory=0
create_kb.write=1

# def create_kb_locator

def create_procedure(kb=None,arguments=None,body=None,environment=None):
    if not kb: kb = current_kb()
    return kb.create_procedure(arguments,body,environment)
create_procedure.enumerator=0
create_procedure.optional=1
create_procedure.read=1
create_procedure.mandatory=0
create_procedure.write=0

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
create_slot.enumerator=0
create_slot.optional=0
create_slot.read=0
create_slot.mandatory=1
create_slot.write=1

def current_kb():
    global CURRENT_KB
    if not CURRENT_KB: CURRENT_KB = meta_kb()
    return CURRENT_KB
current_kb.enumerator=0
current_kb.optional=0
current_kb.read=1
current_kb.mandatory=0
current_kb.write=0

# def decontextualize
# def delete_facet
# def delete_frame
# def delete_slot
# def detach_facet
# def detach_slot
#    ... many missing enumerators ...
# def enumerate_kb_individuals
# def enumerate_kb_roots
# def enumerate_kb_slots
# def enumerate_kb_types
# def enumerate_kbs
# def enumerate_kbs_of_type
# def enumerate_list
# def enumerate_slot_facets
# def enumerate_slot_values
# def enumerate_slot_values_in_detail
# def eql_in_kb
# def equal_in_kb
# def equalp_in_kb

def establish_connection(connection_type,initargs=None):
    return connection_type(initargs)
establish_connection.enumerator=0
establish_connection.optional=1
establish_connection.read=1
establish_connection.mandatory=0
establish_connection.write=0

# def expunge_kb
# def facet_has_value_p
# def facet_p
# def fetch

def find_kb(name_or_kb_or_kb_locator,connection = None):
    if not connection: connection = local_connection()
    return connection.find_kb(name_or_kb_or_kb_locator)
find_kb.enumerator=0
find_kb.optional=1
find_kb.read=1
find_kb.mandatory=0
find_kb.write=0

# def find_kb_locator
# def find_kb_of_type
# def follow_slot_chain
# def frame_has_slot_p

def frame_in_kb_p(thing, kb=None, kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.frame_in_kb_p(thing,kb_local_only_p)
frame_in_kb_p.enumerator=0
frame_in_kb_p.optional=1
frame_in_kb_p.read=1
frame_in_kb_p.mandatory=0
frame_in_kb_p.write=0

# def frs_name
# def get_behaviour_supported_values
# def get_behaviour_values

def get_class_instances(klass,kb=None,inference_level=Node._taxonomic,
                        number_of_values = Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_class_instances(klass,inference_level,
                                  number_of_values,kb_local_only_p)
get_class_instances.enumerator=1
get_class_instances.optional=0
get_class_instances.read=1
get_class_instances.mandatory=1
get_class_instances.write=0

def get_class_subclasses(klass, kb=None, inference_level=Node._taxonomic,
                         number_of_values=Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_class_subclasses(klass,inference_level,number_of_values,
                                   kb_local_only_p)
get_class_subclasses.enumerator=1
get_class_subclasses.optional=0
get_class_subclasses.read=1
get_class_subclasses.mandatory=1
get_class_subclasses.write=0

def get_class_superclasses(klass, kb=None, inference_level=Node._taxonomic,
                           number_of_values=Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_class_superclasses(klass,
                                     inference_level=inference_level,
                                     number_of_values=number_of_values,
                                     kb_local_only_p=kb_local_only_p)
get_class_superclasses.enumerator=1
get_class_superclasses.optional=0
get_class_superclasses.read=1
get_class_superclasses.mandatory=1
get_class_superclasses.write=0

# def get_classes_in_domain_of
# def get_facet_value
# def get_facet_values
# def get_facet_values_in_detail
# def get_frame_details
# def get_frame_handle

def get_frame_in_kb(thing,kb=None,error_p=1,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_in_kb(thing,kb_local_only_p)
get_frame_in_kb.enumerator=0
get_frame_in_kb.optional=0
get_frame_in_kb.read=1
get_frame_in_kb.mandatory=1
get_frame_in_kb.write=0

def get_frame_name(frame,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_name(frame,kb_local_only_p=kb_local_only_p)
get_frame_name.enumerator=0
get_frame_name.optional=0
get_frame_name.read=1
get_frame_name.mandatory=1
get_frame_name.write=0

def get_frame_pretty_name(frame,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_pretty_name(frame,kb_local_only_p=kb_local_only_p)
get_frame_pretty_name.enumerator=0
get_frame_pretty_name.optional=0
get_frame_pretty_name.read=1
get_frame_pretty_name.mandatory=1
get_frame_pretty_name.write=0

def get_frame_sentences(frame, kb=None, number_of_values=Node._all,
                        okbc_sentences_p=1,value_selector=Node._either,
                        kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_sentences(frame,number_of_values,okbc_sentences_p,
                                  value_selector,kb_local_only_p)
get_frame_sentences.enumerator=0
get_frame_sentences.optional=1
get_frame_sentences.read=1
get_frame_sentences.mandatory=0
get_frame_sentences.write=0

def get_frame_slots(frame, kb=None, inference_level=Node._taxonomic,
                    slot_type=Node._all, kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_frame_slots(frame,inference_level,slot_type,
                              kb_local_only_p)
get_frame_slots.enumerator=1
get_frame_slots.optional=0
get_frame_slots.read=1
get_frame_slots.mandatory=1
get_frame_slots.write=0

def get_frame_type(thing, kb=None, inference_level=Node._taxonomic,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_frame_type(thing,kb_local_only_p)
get_frame_type.enumerator=0
get_frame_type.optional=1
get_frame_type.read=1
get_frame_type.mandatory=0
get_frame_type.write=0

# def get_frames_matching
# def get_frames_with_facet_value
# def get_frames_with_slot_value

def get_instance_types(frame, kb=None, inference_level=Node._taxonomic,
                       number_of_values = Node._all, kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_instance_types(frame, inference_level,
                                 number_of_values, kb_local_only_p)
get_instance_types.enumerator=1
get_instance_types.optional=0
get_instance_types.read=1
get_instance_types.mandatory=1
get_instance_types.write=0

def get_kb_classes(kb=None,
                   selector = Node._system_default,
                   kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_classes(selector,kb_local_only_p)
get_kb_classes.enumerator=1
get_kb_classes.optional=1
get_kb_classes.read=1
get_kb_classes.mandatory=0
get_kb_classes.write=0

def get_kb_direct_children(kb=None):
    if not kb: kb = current_kb()
    return kb.get_kb_direct_children()
get_kb_direct_children.enumerator=1
get_kb_direct_children.optional=1
get_kb_direct_children.read=1
get_kb_direct_children.mandatory=0
get_kb_direct_children.write=0

def get_kb_direct_parents(kb=None):
    if not kb: kb = current_kb()
    return kb.get_kb_direct_parents()
get_kb_direct_parents.enumerator=1
get_kb_direct_parents.optional=1
get_kb_direct_parents.read=1
get_kb_direct_parents.mandatory=0
get_kb_direct_parents.write=0

def get_kb_facets(kb=None,
                  selector = Node._system_default,
                  kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_facets_internal(selector, kb_local_only_p)
get_kb_facets.enumerator=1
get_kb_facets.optional=1
get_kb_facets.read=1
get_kb_facets.mandatory=0
get_kb_facets.write=0

def get_kb_frames(kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.get_kb_frames(kb_local_only_p)
get_kb_frames.enumerator=1
get_kb_frames.manadatory=1
get_kb_frames.read=1
get_kb_frames.write=0
get_kb_frames.optional=0

def get_kb_individuals(kb=None,
                       selector = Node._system_default,
                       kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_individuals(selector,kb_local_only_p)
get_kb_individuals.optional=1
get_kb_individuals.read=1
get_kb_individuals.enumerator=1
get_kb_individuals.mandatory=0
get_kb_individuals.write=0

# def get_kb_roots

def get_kb_slots(kb=None,
                 selector = Node._system_default,
                 kb_local_only_p=None):
    if not kb: kb = current_kb()
    return kb.get_kb_slots_internal(selector,kb_local_only_p)
get_kb_slots.optional=1
get_kb_slots.read=1
get_kb_slots.enumerator=1
get_kb_slots.write=0
get_kb_slots.mandatory=0

# def get_kb_type
# def get_kb_types
# def get_kbs

def get_procedure(name,kb=None):
    if not kb: kb = current_kb()
    return kb.get_procedure(name)
get_procedure.optional=1
get_procedure.read=1
get_procedure.write=0
get_procedure.mandatory=0
get_procedure.enumerator=0

def get_slot_facets(frame,slot,kb=None,
                   inference_level = Node._taxonomic,
                   slot_type = Node._own,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.get_slot_facets(frame,slot,
                              inference_level,slot_type,
                              kb_local_only_p)
get_slot_facets.mandatory=1
get_slot_facets.read=1
get_slot_facets.enumerator=1
get_slot_facets.write=0
get_slot_facets.optional=0

# def get_slot_type

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
get_slot_value.optional=1
get_slot_value.read=1
get_slot_value.enumerator=1
get_slot_value.write=0
get_slot_value.mandatory=0

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
get_slot_values.optional=1
get_slot_values.read=1
get_slot_values.enumerator=1
get_slot_values.mandatory=0
get_slot_values.write=0

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
get_slot_values_in_detail.enumerator=1
get_slot_values_in_detail.optional=0
get_slot_values_in_detail.read=1
get_slot_values_in_detail.mandatory=1
get_slot_values_in_detail.write=0

def goto_kb(kb):
    global CURRENT_KB
    CURRENT_KB = kb
goto_kb.enumerator=0
goto_kb.optional=1
goto_kb.read=0
goto_kb.mandatory=0
goto_kb.write=1

# def has_more

def individual_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.individual_p(thing,kb_local_only_p)
individual_p.enumerator=0
individual_p.optional=1
individual_p.read=1
individual_p.mandatory=0
individual_p.write=0

def instance_of_p(thing,klass,kb=None,                  
                  inference_level=Node._taxonomic,
                  kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.instance_of_p(thing,klass,inference_level,kb_local_only_p)
instance_of_p.enumerator=0
instance_of_p.optional=1
instance_of_p.read=1
instance_of_p.mandatory=0
instance_of_p.write=0

# def kb_modified_p

def kb_p(thing):
    return isinstance(thing,KB)
kb_p.enumerator=0
kb_p.optional=1
kb_p.read=1
kb_p.mandatory=0
kb_p.write=0

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
local_connection.enumerator=0
local_connection.optional=0
local_connection.read=1
local_connection.mandatory=0
local_connection.write=0

# def member_behaviour_values_p
# def member_facet_value_p
# def member_slot_value_p

def meta_kb(connection = None):
    if not connection: connection = local_connection()
    return connection.meta_kb()
meta_kb.enumerator=0
meta_kb.optional=1
meta_kb.read=1
meta_kb.mandatory=0
meta_kb.write=0

# def next
# def okbc_condition_p

def open_kb(kb_locator,
            kb_type = None,
            connection = None,
            error_p = 1):
    if not connection: connection = local_connection()
    return connection.open_kb(kb_locator,kb_type,error_p)
open_kb.enumerator=0
open_kb.optional=0
open_kb.read=0
open_kb.mandatory=1
open_kb.write=1

def openable_kbs(kb_type=None,connection = None,place=None):
    if not connection: connection = local_connection()
    return connection.openable_kbs(kb_type,place)
openable_kbs.enumerator=0
openable_kbs.optional=0
openable_kbs.read=1
openable_kbs.mandatory=1
openable_kbs.write=0

# def prefetch
# def primitive_p

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
print_frame.enumerator=0
print_frame.optional=1
print_frame.read=1
print_frame.mandatory=0
print_frame.write=0

def procedure_p(thing):
    return type(thing) == type(lambda a:a)
    #return isinstance(thing,PROCEDURE)
procedure_p.enumerator=0
procedure_p.optional=0
procedure_p.read=1
procedure_p.mandatory=0
procedure_p.write=0

# def put_behavior_values

def put_class_superclasses(klass,new_superclasses,kb=0,kb_local_only_p=0):
    if not kb: kb = current_kb()
    kb.put_class_superclasses(klass,new_superclasses,kb_local_only_p)
put_class_superclasses.enumerator=0
put_class_superclasses.optional=0
put_class_superclasses.read=0
put_class_superclasses.mandatory=1
put_class_superclasses.write=1

# def put_facet_value
# def put_facet_values
# def put_frame_details
# def put_frame_name

def put_frame_pretty_name(frame,name,kb=0,kb_local_only_p=0):
    if not kb: kb = current_kb()
    kb.put_frame_pretty_name(frame,name,kb_local_only_p)
put_frame_pretty_name.enumerator=0
put_frame_pretty_name.optional=0
put_frame_pretty_name.read=0
put_frame_pretty_name.mandatory=1
put_frame_pretty_name.write=1

def put_instance_types(frame,new_types,kb=0,kb_local_only_p = 0):
    if not kb: kb = current_kb()
    kb.put_instance_types(frame,new_types,kb_local_only_p)
put_instance_types.enumerator=0
put_instance_types.optional=0
put_instance_types.read=0
put_instance_types.mandatory=1
put_instance_types.write=1

def put_slot_value(frame,slot, value,
                   kb = None,
                   slot_type=Node._own,
                   value_selector = Node._known_true,
                   kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.put_slot_value(frame,slot,value,slot_type,
                             value_selector,kb_local_only_p)
put_slot_value.enumerator=0
put_slot_value.optional=1
put_slot_value.read=0
put_slot_value.mandatory=0
put_slot_value.write=1

def put_slot_values(frame,slot, values,
                    kb = None,
                    slot_type=Node._own,
                    value_selector = Node._known_true,
                    kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.put_slot_values(frame,slot,values,slot_type,
                              value_selector,kb_local_only_p)
put_slot_values.enumerator=0
put_slot_values.optional=0
put_slot_values.read=0
put_slot_values.mandatory=1
put_slot_values.write=1

def register_procedure(name,procedure,kb=None):
    if not kb: kb = current_kb()
    kb.register_procedure(name,procedure)
register_procedure.enumerator=0
register_procedure.optional=1
register_procedure.read=0
register_procedure.mandatory=0
register_procedure.write=1

# def remove_class_superclass
# def remove_facet_value
# def remove_instance_type
# def remove_local_facet_values
# def remove_local_slot_values
# def remove_slot_value
# def rename_facet
# def rename_slot
# def replace_facet_value
# def replace_slot_value
# def revert_kb

def save_kb(kb=None,error_p=1):
    if not kb: kb = current_kb()
    return kb.save_kb(error_p=error_p)
save_kb.enumerator=0
save_kb.optional=0
save_kb.read=0
save_kb.mandatory=1
save_kb.write=1

def save_kb_as(new_name_or_locator,kb=None,error_p = 1):
    if not kb: kb = current_kb()
    kb.save_kb_as(new_name_or_locator,error_p=error_p)
save_kb_as.enumerator=0
save_kb_as.optional=0
save_kb_as.read=0
save_kb_as.mandatory=1
save_kb_as.write=1

# def slot_has_facet_p
# def slot_has_value_p

def slot_p(thing,kb=None,kb_local_only_p=0):
    if not kb: kb = current_kb()
    return kb.slot_p(thing,kb_local_only_p)
slot_p.enumerator=0
slot_p.optional=1
slot_p.read=1
slot_p.mandatory=0
slot_p.write=0

def subclass_of_p(subclass,superclass,kb=None,
                  inference_level=Node._taxonomic,
                  kb_local_only_p = 0):
    if not kb: kb = current_kb()
    return kb.subclass_of_p(subclass,superclass,
                            inference_level,kb_local_only_p)
subclass_of_p.enumerator=0
subclass_of_p.optional=1
subclass_of_p.read=1
subclass_of_p.mandatory=0
subclass_of_p.write=0

def superclass_of_p(superclass,subclass,kb=None,
                    inference_level=Node._taxonomic):
    if not kb: kb = current_kb()    
    return kb.subclass_of_p(superclass,subclass,
                            inference_level,kb_local_only_p)
superclass_of_p.enumerator=0
superclass_of_p.optional=1
superclass_of_p.read=1
superclass_of_p.mandatory=0
superclass_of_p.write=0

# def tell
# def tellable
# def type_of_p

def unregister_procedure(name,kb=None):
    if not kb: kb = current_kb()
    kb.unregister_procedure(name)
unregister_procedure.enumerator=0
unregister_procedure.optional=1
unregister_procedure.read=0
unregister_procedure.mandatory=0
unregister_procedure.write=1

# def untell
# value_as_string


##########################################
#   Methods outside of the OKBC spec
##########################################

def put_direct_parents(parent_kbs,kb=None):
    if not kb: kb = current_kb()
    kb.put_direct_parents(parent_kbs)
