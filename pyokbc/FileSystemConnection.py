
from PyOkbc import *
import os

class FileSystemConnection(Connection):
    def __init__(connection,initargs=None):
        connection._initargs = initargs
        connection._default_place = initargs['default_place']
        connection._meta_kb = None        
        #Connection.__init__(connection,initargs)
        connection._meta_kb = TupleKb(connection._default_place,
                                      connection = connection)
        from PyKb import PyKb
        connection._default_kb_type = PyKb

    def openable_kbs(connection,kb_type,place=None):
        if not place: place = connection._default_place
        warn("openable_kbs doing listdir of"+place)
        entries = os.listdir(place)
        rets = []
        for e in entries:
            try:
                if e[-5:] == '.pykb':
                    rets.append(e)
            except:
                pass
        rets.sort()
        return rets

    def _obtain_raw_kb(connection,filename,place):
        if place == '': # FIXME this should be passed in!
            #place = os.getcwd() + '/know/'
            place = connection._default_place        
        fname = place+'/'+filename # FIXME should os.pathjoin be used?
        f = open(fname)
        lines = f.readlines()
        f.close()
        return lines
