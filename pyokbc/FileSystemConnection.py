
from PyOkbc import *
from OkbcConditions import *
import dircache
import os
from FileSystemKb import *
import string

def _make_allowed_fname(allowed_place,kb_locator):
    #if DEBUG: print "make_fname",frag
    print "_make_allowed_fname",allowed_place,kb_locator
    fullpath = os.path.join(allowed_place,kb_locator)
    normpath = os.path.normpath(fullpath)
    #if DEBUG: print "normpath =",normpath
    if normpath.find(allowed_place) != 0:
        raise "Illegal path requested",\
              "%s not in %s" % (normpath,allowed_place)
    return normpath


class FileSystemConnection(Connection):
    def __init__(connection,initargs=None):
        connection._initargs = initargs
        connection._default_place = initargs['default_place']
        connection._path = string.split(connection._default_place,
                                                ':')
        connection._meta_kb = None
        #Connection.__init__(connection,initargs)
        connection._meta_kb = FileSystemKb(connection._default_place,
                                           connection = connection)
        connection._meta_kb._add_frame_to_store(Node._primordial_kb)
        from PyKb import PyKb
        connection._default_kb_type = PyKb
        connection._ignore_tildes = 1


    def _find_kbs_in(connection,place):
        rets = []
        entries = dircache.listdir(place)        
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
        return rets

    def openable_kbs(connection,kb_type,place=None):
        if not place: place = connection._default_place
        warn("openable_kbs doing listdir of "+place)


        rets = ['PRIMORDIAL_KB']
        for place in connection._path:
            rets.extend(connection._find_kbs_in(place))

        rets.sort()
        return rets

    def _lines_and_stats(connection,filename,place):
        path = connection._path
        print "_lines_and_stats place =",place,filename
        if place != '':
            path = [place]
        for a_place in path:
            if __builtins__.has_key('nooron_root'): # FIXME bad hack
                fname = _make_allowed_fname(a_place,filename)
            else:
                fname = os.path.join(place,filename)
            try:
                f = open(fname)
                lines = f.readlines()
                f.close()
                break
            except:
                continue
        if lines:
            st = os.stat(fname)
            stats = {'UID':st[4],
                     'GID':st[5],
                     'SIZE':st[6],
                     'ATIME':st[7],
                     'MTIME':st[8],
                     'CTIME':st[9]}
            stats['ModificationTime'] = stats['MTIME']
            stats['CreationTime'] =     stats['CTIME']
            stats['AccessTime'] =       stats['ATIME']
            return (lines,stats)
        else:
            raise KbNotFound,(filename,path)            
