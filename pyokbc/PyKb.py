
import string

from PyOkbc import *
import string
import os

EMIT_STRINGS_NOT_VARS = 1

def var_name_for_emit(frame):
    out = string.replace(get_frame_name(frame),' ','_')
    if EMIT_STRINGS_NOT_VARS:
        return "'%s'" % out
    else:
        return out

def emit_value(val):
    if type(val) == type(''):
        if string.find(val,"'") + string.find(val,"\n") > -2:
            return '"""%s"""' % val
        return "'%s'" % val
    elif EMIT_STRINGS_NOT_VARS and isinstance(val,FRAME):
        return "'"+str(val)+"'"
    else:
        return str(val)
    
def to_slot_spec(frame,slot,slot_type):
    #print "to_slot_spec(",frame,slot,slot_type,")"
    slot_value_spec = ''
    for slot_value in get_slot_values(frame,slot,slot_type=slot_type)[0]:
        if type(slot_value) in (type(()),type([])) \
           and slot_value[0] == Node._default:
            slot_value_prefix = "(Node._default, "
            slot_value_suffix = ")"
            slot_value = slot_value[1]
        else:
            slot_value_prefix = slot_value_suffix = ""

        if type(slot_value) in (type(()),type([])):
            for val in slot_value:
                slot_value_spec = slot_value_spec + emit_value(val) + ","
            if slot_value:
                slot_value_spec = slot_value_spec[:-1]
        else:
            slot_value_spec = slot_value_spec + emit_value(slot_value) + ", "
    #if slot_value_spec[-2:] == ', ':
    slot_value_spec = slot_value_spec[:-2]
    #else:
    #    die("we get here")
    return "[" + emit_value(slot) + ", " + slot_value_spec + "]"

class PyKb(AbstractFileKb):
    _kb_type_file_extension = 'pykb'
    def __init__(self,filename,place='',connection=None,name=None):
        if name == None:
            name = filename
        #print name,filename
        ext = self._kb_type_file_extension 
        if not (len(filename) > len(ext) and \
           filename[-1 * len(ext):] == ext):
            filename = filename + '.' + ext
        raw_kb = connection._obtain_raw_file(filename,place)
        AbstractFileKb.__init__(self,name,connection=connection)
        #if place == '': # FIXME this should be passed in!
            #place = os.getcwd() + '/know/'
        #    place = connection._default_place        
        #fname = place+filename # FIXME should os.pathjoin be used?
        prev_kb = current_kb()
        goto_kb(self)

        try:
            exec(string.join(raw_kb,""))
        except exceptions.SyntaxError,e:
            raise GenericError,str(e)+ " of "+str(filename)
        goto_kb(prev_kb)

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
        lines = []
        frame_name = kb.get_frame_name(frame)
        var_name = var_name_for_emit(frame)
        frame_type = kb.get_frame_type(frame)
        frame_type_string = str(frame_type)[1:]
        if EMIT_STRINGS_NOT_VARS:
            assignment_line = ""
        else:
            assignment_line = var_name + " = "            
        assignment_line = assignment_line \
                          + "create_" \
                          + frame_type_string \
                          + "("
        indent_str = " " * len(assignment_line)
        assignment_line = assignment_line + "'" + frame_name + "'"
        lines.append(assignment_line)

        line = "direct_types=["
        got_one = 0
        for klass in kb.get_instance_types(frame,
                                           inference_level=Node._direct)[0]:
            line = line + var_name_for_emit(klass) + ","
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "direct_superclasses=["
        got_one = 0
        if kb.class_p(frame):
            #print frame,"is class_p"
            get_supers = kb.get_class_superclasses
            for klass in get_supers(frame,
                                    inference_level=Node._direct)[0]:
                line = line + var_name_for_emit(klass) + ","
                got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "own_slots=["
        got_one = 0
        local_indent_str = indent_str + " " * len(line)
        for slot in get_frame_slots(frame,slot_type=Node._own)[0]:
            line = line + to_slot_spec(frame,slot,Node._own) \
                   + ",\n" + local_indent_str
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "template_slots=["
        got_one = 0
        local_indent_str = indent_str + " " * len(line)
        for slot in get_frame_slots(frame,slot_type=Node._template,
                                    inference_level=Node._direct)[0]:
            line = line + to_slot_spec(frame,slot,Node._template) \
                   + ",\n" + local_indent_str
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "pretty_name="
        pretty_name = kb.get_frame_pretty_name(frame)
        if pretty_name != None: lines.append(line+emit_value(pretty_name))

        comma_and_indent = ",\n"+indent_str
        out =  string.join(lines,comma_and_indent) + ")\n"
        if stream:
            print out
            return None
        else:
            return out

