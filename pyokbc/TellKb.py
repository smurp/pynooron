
import string

from PyOkbc import *
import string


class TellKb(AbstractFileKb):
    _kb_type_file_extension = 'tellkb'
    def __init__(self,filename,place='',connection=None):
        raw_kb = connection._obtain_raw_file(filename,place)
        AbstractFileKb.__init__(self,filename,connection=connection)
        prev_kb = current_kb()
        goto_kb(self)
        raise "ParsingNotImplemented",filename
        #exec(string.join(raw_kb,"\n"))
        goto_kb(prev_kb)
