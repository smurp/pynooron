
from PyOkbc import *
from OkbcConditions import *
import dircache
import os
from FileSystemKb import *
import string

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

            if not (connection._ignore_tildes and e[-1] == '~') and \
               not (e[0] == e[-1] and e[0] == '#') or \
               os.path.isdir(os.path.join(place,e)):

                if splits[-1] in pyokbc_mimetypes.keys():
                    just_the_name = string.join(list(splits[:-1]),'')
                    rets.append(just_the_name)
                else:
                    rets.append(e)
        rets.sort()
        return rets

    def _lines_and_stats(connection,filename,place):
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
        st = os.stat(fname)
        stats = {'UID':st[4],
                 'GID':st[5],
                 'SIZE':st[6],
                 'ATIME':st[7],
                 'MTIME':st[8],
                 'CTIME':st[9]}
        return (lines,stats)
