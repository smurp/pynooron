
__version__='$Revision: 1.23 $'[11:-2]
__cvs_id__ ='$Id: PyKb.py,v 1.23 2008/09/26 20:45:33 smurp Exp $'

from PyOkbc import *
from CachingMixin import CachingMixin
import string
import os
from debug_tools import timed

"""PyKb is a rather simple file-based PyOKBC backend which simply uses Python
source code as its file format.  The peculiar decision to bootstrap development
of PyOKBC with this format was grounded in expediency: it means that no parsing
needs to be done and it means that OKBC Procedures can (temporarily) be
written in Python, giving us some of the advantages of such Procedures without
actually having to implement an efficient, secure mini-lisp.  The intention is
that the use of PyKb will be temporary, and that it will be replaced by TellKb
as soon as possible.  There is nothing particularly wrong with PyKb as a file
format at the outset of the Nooron project, but later -- when portable knowledge
and logic is required -- more intrinsically secure approaches will be required.
"""

EMIT_STRINGS_NOT_VARS = 1

def safely_quoted_python_string(unsafe): # BUGGED large security flaw
    if string.find(unsafe,"'") + string.find(unsafe,"\n") > -2:
        return '"""%s"""' % unsafe
    return "'%s'" % str(unsafe)  

def var_name_for_emit(frame):
    out = string.replace(get_frame_name(frame),' ','_')
    if EMIT_STRINGS_NOT_VARS:
        return "'%s'" % out
    else:
        return out

def emit_value(val):
    if type(val) == type(''):
        return safely_quoted_python_string(val)
    elif EMIT_STRINGS_NOT_VARS and isinstance(val,FRAME):
        return safely_quoted_python_string(val)
    else:
        return str(val)
    

class PyKb(AbstractFileKb,CachingMixin):
    _kb_type_file_extension = 'pykb'
    def __init__(self,filename_or_kb_locator,
                 place='',connection=None,name=None,
                 initargs = {}):
        self._name = 'never_assigned'
        if type(filename_or_kb_locator) == dict:
            from urlparse import urlparse
            import os.path
            self._locator = filename_or_kb_locator
            (scheme,netloc,path,param,query,fragment) = urlparse(self._locator['file_uri'])
            filename = os.path.basename(path)
            place = os.path.basename(path)
            self._name = self._locator['kb_name']
            self._file_uri = self._locator['file_uri']
            self._filename = filename #self._file_uri
            filename = self._file_uri # should convert from uri
            name = self._name
        elif type(filename_or_kb_locator) == str:
            self._locator = filename_or_kb_locator
            self._name = filename_or_kb_locator
            self._file_uri = filename_or_kb_locator
            self._filename = filename_or_kb_locator
            filename = self._file_uri # should convert from uri
            name = self._name            
        else:
            raise "expecting filename_or_kb_locator as dict, not " + \
                str(filename_or_kb_locator) + \
                'of type' + str(type(filename_or_kb_locator))
        
        self._set_place(place)
        self._connection = connection
        self._opened = False
        AbstractFileKb.__init__(self,name,connection=connection)
        CachingMixin.__init__(self)

    #@timed
    def __str__(self):
        #return self._name
        return self._name.replace('.pykb','')

    @timed
    def open_kb_internal(self,
                         kb_type = None,
                         error_p = True):
        if self._opened:
            return self
        connection = self._connection
        name = self._name
        (raw_kb,stats) = connection._lines_and_stats(self._filename,
                                                     self._place)

        #AbstractFileKb.__init__(self,name,connection=connection)
        #CachingMixin.__init__(self)

        prev_kb = current_kb()
        goto_kb(self)
        orig_allow_caching_p = self.allow_caching_p()
        self._allow_caching_p = 0
        self._changes_register_as_modifications_p = 0
        for (key,val) in stats.items():
            self.put_slot_value(self,str(key),val)
        
        try:
            whole = string.join(raw_kb,"")
            stanzas = whole.split('\n\n')
            stanza = whole
            #for stanza in stanzas:
            #print stanza
            exec(stanza)
        except exceptions.SyntaxError,e:
            #raise GenericError,str(e)+ " of "+str(filename)
            #print stanza
            raise GenericError,str(e)+ " in "+ stanza
        #return self._changes_register_as_modifications_p        
        self._changes_register_as_modifications_p = 1
        #print "setting changes_register... ",self.changes_register_as_modifications_p(),"in",self
        self._allow_caching_p = orig_allow_caching_p
        goto_kb(prev_kb)
        self._opened = True
        return self

    def _preamble(kb):
        return '# -*-mode: python -*-\n'

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

        line = "pretty_name="
        pretty_name = kb.get_frame_pretty_name(frame)
        if pretty_name != None: lines.append(line+emit_value(pretty_name))


        line = "direct_types=["
        got_one = 0
        for klass in kb.get_instance_types(frame,
                                           inference_level=Node._direct)[0]:
            klass_name =  var_name_for_emit(klass)
            if not (klass_name in ["':INDIVIDUAL'","':SLOT'","':CLASS'",
                                   "':KB'","':THING'"]):
                # FIXME the above test is a kludge re create_frame_internal
                line = line + klass_name + ","
                got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "direct_superclasses=["
        got_one = 0
        if kb.class_p(frame):
            #print frame,"is class_p"
            get_supers = kb.get_class_superclasses
            for klass in get_supers(frame,
                                    inference_level=Node._direct)[0]:
                klass_name =  var_name_for_emit(klass)
                if not (klass_name in ["':THING'"]):
                    line = line + var_name_for_emit(klass) + ","
                    got_one = 1
        if got_one: lines.append(line[:-1]+"]")

        line = "own_slots=["
        got_one = 0
        local_indent_str = indent_str + " " * len(line)
        own_slots = kb.get_frame_slots(frame,slot_type=Node._own)[0]
        #print frame,own_slots
        if ":DOCUMENTATION" in own_slots:
            doc_p = 1
            own_slots.remove(':DOCUMENTATION')
        else:
            doc_p = None
        own_slots.sort()
        for slot in own_slots:
            #if not kb.instance_of_p(slot,':TRANSIENT_SLOT',
            #                        inference_level=Node._direct)[0]:
            line = line + kb._to_slot_spec(frame,slot,Node._own) \
                   + ",\n" + local_indent_str
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")
            
        line = "template_slots=["
        got_one = 0
        local_indent_str = indent_str + " " * len(line)
        for slot in kb.get_frame_slots(frame,slot_type=Node._template,
                                       inference_level=Node._direct)[0]:
            line = line + kb._to_slot_spec(frame,slot,Node._template) \
                   + ",\n" + local_indent_str
            got_one = 1
        if got_one: lines.append(line[:-1]+"]")


        if doc_p:
            docs = kb.get_slot_value(frame,':DOCUMENTATION',
                                     inference_level=Node._direct)[0]
            lines.append('doc="""'+docs+'"""')


        comma_and_indent = ",\n"+indent_str
        out =  string.join(lines,comma_and_indent) + ")\n"
        if stream:
            print out
            return None
        else:
            return out


    def _to_slot_spec(kb,frame,slot,slot_type):
        #print "to_slot_spec(",frame,slot,slot_type,")"
        slot_value_spec = ''
        for slot_value in kb.get_slot_values(frame,slot,slot_type=slot_type)[0]:
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
    #            if slot_value:
    #                slot_value_spec = slot_value_spec[:-1]
            else:
                slot_value_spec = slot_value_spec + emit_value(slot_value) + ", "
        #if slot_value_spec[-2:] == ', ':
        slot_value_spec = slot_value_spec[:-2]
        return "[" + emit_value(slot) + ", " + slot_value_spec + "]"


    def _safe_value_list(kb,frame,slot,slot_type):
        quoted_slot_values = []
        for slot_value in kb.get_slot_values(frame,slot,slot_type=slot_type)[0]:
            quoted_slot_values.append(emit_value(slot_value))

        return "[%s]" % string.join(quoted_slot_values,", ")


    def _print_kb_own_attributes(kb):
        return kb._print_put_direct_parents() + \
               kb._print_put_instance_types() + \
               kb._print_put_frame_pretty_name() +\
               kb._print_put_slot_values() 

    def _print_put_direct_parents(kb):
        parent_name_list = []
        for parent in kb.get_kb_direct_parents():
            parent_name_list.append("'" + str(parent) + "'")
        if parent_name_list.count("'PRIMORDIAL_KB'"):
            parent_name_list.remove("'PRIMORDIAL_KB'")
        if parent_name_list:
            return "put_direct_parents([%s])\n" % string.join(parent_name_list,',')
        return ''

    def _print_put_instance_types(kb):
        instance_type_list = []
        for my_type in kb.get_instance_types(kb,
                                             inference_level=Node._direct)[0]:
            instance_type_list.append("'" + str(my_type) + "'")
        if instance_type_list.count("':KB'"):
            instance_type_list.remove("':KB'")
        if instance_type_list:
            return "put_instance_types(current_kb(),[%s])\n" % \
                   string.join(instance_type_list,',')
        return ''

    def _print_put_frame_pretty_name(kb):
        pname = kb.get_frame_pretty_name(kb)
        if pname:
            return 'put_frame_pretty_name(current_kb(),"""%s""")\n' % pname
        return ''


    def _print_put_slot_values(kb):
        calls = []
        for slot in kb.get_frame_slots(kb,slot_type=Node._own)[0]:
            if not kb.instance_of_p(slot,':TRANSIENT_SLOT',
                                    inference_level=Node._direct)[0]:
                calls.append("put_slot_values(current_kb(),%s,%s)\n" % \
                             (safely_quoted_python_string(slot),
                              kb._safe_value_list(kb,slot,Node._own)))
        if calls:
            return string.join(calls,'\n')
        return ''
