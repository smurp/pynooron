
import string

from PyOkbc import *
from CachingMixin import *
import string
import os
import StringIO

def word2int(word):
    assert len(word) == 4
    mult = 1L
    val = 0L
#    print "word = ",word
    for i in word:
        val = ord(i) * mult + val
#        print val,
        mult = mult * 256
#    print 
    return val

def pretty_name_to_name(pretty_name):
    retval = string.replace(pretty_name,' ','')
    retval = string.replace(retval,'.','')
    return retval

class BrainKb(AbstractFileKb,CachingMixin):
    _kb_type_file_extension = 'brn'
    def __init__(self,filename,place='',connection=None,name=None):
        if not place:
            print "place NOT SET FOR",filename
        self._place = place
        if name == None:
            name = filename
        self._name = name
        #print name,filename
        ext = self._kb_type_file_extension 
        if not (len(filename) > len(ext) and \
           filename[-1 * len(ext):] == ext):
            filename = filename + '.' + ext
        (raw_kb,stats) = connection._lines_and_stats(filename,place)
        AbstractFileKb.__init__(self,name,connection=connection)
        CachingMixin.__init__(self)
        #if place == '': # FIXME this should be passed in!
            #place = os.getcwd() + '/know/'
        #    place = connection._default_place        
        #fname = place+filename # FIXME should os.pathjoin be used?
        prev_kb = current_kb()
        goto_kb(self)
        orig_allow_caching_p = self.allow_caching_p()
        self._allow_caching_p = 0
        self._changes_register_as_modifications_p = 0
        for (key,val) in stats.items():
            self.put_slot_value(self,str(key),val)
        
        try:
            whole = string.join(raw_kb,"")
            stanza = whole
            self._parse_brain(whole)
        except exceptions.SyntaxError,e:
            #raise GenericError,str(e)+ " of "+str(filename)
            #print stanza
            raise GenericError,str(e)+ " in "+str(filename)
        #return self._changes_register_as_modifications_p        
        self._changes_register_as_modifications_p = 1
        self._allow_caching_p = orig_allow_caching_p
        goto_kb(prev_kb)

    
    def _parse_brain(self,stuff):
        #print whole
        whole = StringIO.StringIO(stuff)
        file_type_hint = whole.read(4)
        assert word2int(file_type_hint) == 638720368
        rec_no = 0
        slots = {}
        classes = {}
        while 1:
            own_slots = []
            classname = ''
            rec_no = rec_no + 1
            record_offset = whole.read(4)
            if not record_offset:
                break
            rec_len = word2int(record_offset)
            #print "Rec %i =================================" % rec_no
            rec = {}
            for sect in ('LINKS','BODY','DUNNO'):
                offset = word2int(whole.read(4))
                #print sect
                value = whole.read(offset)
                #print value
                #print
                #continue
                rec[sect] = value
            for line in string.split(rec['BODY'],'\r\n'):
                if line:
                    try:
                        key,val = string.split(line,': ',1)
                    except:
                        continue
                    slotname = pretty_name_to_name(key)
                    #print "slotname =",slotname
                    if not slots.has_key(slotname):
                        slots[slotname] = key
                    if not classname:
                        # first 'slot' is really the class!?!
                        classname = slotname
                        # first slot value is really the instance pretty_name
                        pretty_name = val
                        if not classes.has_key(classname):
                            classes[classname] = \
                                   create_class(classname,
                                                pretty_name=key)
                    else:
                        own_slots.append([slotname,val])
            name = pretty_name_to_name(pretty_name)
            #print "create individual(%s,%s,direct_types=[%s],own_slots=%s)" % (name,pretty_name,classname,str(own_slots))
            self.create_individual(name,pretty_name=pretty_name,
                                   direct_types=[classname],
                                   own_slots=own_slots)





    def _old_parse_brain(self,stuff):
        self._brn_file_header = whole[0:4]
        print "file_header =",self._brn_file_header
        fpos = 4
        more = 1
        while more:
            record_offset = whole[fpos:fpos+4]
            fpos = fpos+4
            rec_len = word2int(record_offset)
            record_body = whole[fpos:fpos+rec_len]
            fpos = fpos + rec_len
            print "== %i %i ==================================="%(fpos,rec_len)
            print record_body
            more == fpos < whole_len
