
import string

from PyOkbc import *
import string


class TellKb(AbstractFileKb):
    _kb_type_file_extension = 'tellkb'
    def __init__(self,filename,place='',meta=None):
        if place == '': # FIXME this should be passed in!
            place = os.getcwd() + "/know/"
        self._name = filename
        AbstractFileKb.__init__(self,filename,kb=meta)
        fname = place+filename
        prev_kb = current_kb()
        goto_kb(self)
        try:
            execfile(fname)
        except IOError:
            raise "CantOpenTellKb",fname + " in " + place
        goto_kb(prev_kb)

