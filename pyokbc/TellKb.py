
import string

from PyOkbc import *
import string


class TellKb(AbstractFileKb):
    _kb_type_file_extension = 'tellkb'
    def __init__(self,filename,place='',connection=None):
        AbstractFileKb.__init__(self,filename,connection=connection)
        raw_kb = connection._obtain_raw_kb(filename,place)
        prev_kb = current_kb()
        goto_kb(self)
        raise "ParsingNotImplemented",filename
        #exec(string.join(raw_kb,"\n"))
        goto_kb(prev_kb)
