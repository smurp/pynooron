
import string


from PyOkbc import *
import string

EMIT_STRINGS_NOT_VARS = 1

def var_name_for_emit(frame):
    out = string.replace(get_frame_name(frame),' ','_')
    if EMIT_STRINGS_NOT_VARS:
        return "'%s'" % out
    else:
        return out

def emit_value(val):
    if type(val) == type(''):
        return '"""%s"""' % val
    elif EMIT_STRINGS_NOT_VARS and isinstance(val,FRAME):
        return "'"+str(val)+"'"
    else:
        return str(val)
    
def to_slot_spec(frame,slot,slot_type):
    slot_value_spec = ''
    #if slot_type == Node._template:
    #dump_frame(frame)
        #print "slot_values:",frame.get_slot_values(slot,slot_type=slot_type)[0]
    slot_value_spec = ''
    for slot_value in frame.get_slot_values(slot,slot_type=slot_type)[0]:
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

class OkbcPythonKb(TupleKb):
    def __init__(self,filename):
        self._name = filename
        TupleKb.__init__(self)
        prev_kb = current_kb()
        goto_kb(self)
        execfile(filename)
        goto_kb(prev_kb)


    def save_kb(kb,error_p = 1):
        for frame in \
            get_kb_facets(kb) + \
            get_kb_slots(kb) + \
            get_kb_classes(kb) + \
            get_kb_individuals(kb):
            print kb.emit_frame(frame)


    def emit_frame(kb,frame):
        lines = []
        frame_name = frame.get_frame_name()
        var_name = var_name_for_emit(frame)
        frame_type = get_frame_type(frame)
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
        for klass in frame.get_instance_types(inference_level=Node._direct)[0]:
            line = line + var_name_for_emit(klass) + ","
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "direct_superclasses=["
        got_one = 0
        if frame.class_p():
            for klass in frame.get_class_superclasses(inference_level=Node._direct)[0]:
                line = line + var_name_for_emit(klass) + ","
                got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "own_slots=["
        got_one = 0
        local_indent_str = indent_str + " " * len(line)
        for slot in frame.get_frame_slots(slot_type=Node._own):
            line = line + to_slot_spec(frame,slot,Node._own) \
                   + ",\n" + local_indent_str
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "template_slots=["
        got_one = 0
        local_indent_str = indent_str + " " * len(line)
        for slot in frame.get_frame_slots(slot_type=Node._template):
            line = line + to_slot_spec(frame,slot,Node._template) \
                   + ",\n" + local_indent_str
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "pretty_name="
        pretty_name = kb.get_frame_pretty_name(frame)
        if pretty_name != None: lines.append(line+emit_value(pretty_name))

        comma_and_indent = ",\n"+indent_str
        return string.join(lines,comma_and_indent) + ")\n"

