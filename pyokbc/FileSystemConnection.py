
from PyOkbc import *
from OkbcConditions import *
import dircache
import os
from FileSystemKb import *

class FileSystemConnection(Connection):
    def __init__(connection,initargs=None):
        connection._initargs = initargs
        connection._default_place = initargs['default_place']
        connection._meta_kb = None
        #Connection.__init__(connection,initargs)
        connection._meta_kb = FileSystemKb(connection._default_place,
                                           connection = connection)
        connection._meta_kb._add_frame_to_cache(Node._primordial_kb)
        from PyKb import PyKb
        connection._default_kb_type = PyKb
        connection._ignore_tildes = 1

    def openable_kbs(connection,kb_type,place=None):
        if not place: place = connection._default_place
        warn("openable_kbs doing listdir of"+place)
        
        entries = dircache.listdir(place)
        
        rets = ['PRIMORDIAL_KB']
        for e in entries:
            splits = os.path.splitext(e)
            try:
                if not (connection._ignore_tildes and e[-1] == '~') and \
                   not (e[0] == e[-1] and e[0] == '#') or \
                   os.path.isdir(os.path.join(place,e)):
                    rets.append(e)
            except:
                pass
        rets.sort()
        return rets

    def _obtain_raw_file(connection,filename,place):
        if place == '': # FIXME this should be passed in!
            #place = os.getcwd() + '/know/'
            place = connection._default_place
        if __builtins__.has_key('nooron_root'): # FIXME bad hack
            fname = nooron_root.make_fname([place,filename])
        else:
            fname = os.path.join(place,filename)
        try:
            f = open(fname)
            lines = f.readlines()
            f.close()
        except:
            raise KbNotFound,(filename,fname)
        return lines
