
from PyOkbc import *
from OkbcConditions import *
import dircache
import os
from FileSystemKb import *
import string

def _make_allowed_fname(allowed_place,kb_locator):
    #if DEBUG: print "make_fname",frag
    #print "_make_allowed_fname",allowed_place,kb_locator
    #print allowed_place,kb_locator
    fullpath = os.path.join(allowed_place,kb_locator)
    normpath = os.path.normpath(fullpath)
    if string.find(kb_locator,'pert') == 0:
        print "LOOKING FOR pert IN",allowed_place,normpath
        
    #if DEBUG: print "normpath =",normpath
    if normpath.find(allowed_place) != 0:
        raise "Illegal path requested",\
              "%s not in %s" % (normpath,allowed_place)
    return normpath

def canonicalize_path(a_path_string):
    retlist = []
    for a_dir in a_path_string.split(':'):
        retlist.append(os.path.abspath(os.path.realpath(os.path.normpath(a_dir))))
    return retlist

class FileSystemConnection(Connection):
    def __init__(connection,initargs=None):
        connection._initargs = initargs
        connection._default_place = initargs['default_place']
        connection._path = canonicalize_path(connection._default_place)

        connection._meta_kb = None
        #Connection.__init__(connection,initargs)
        connection._meta_kb = FileSystemKb(connection._default_place,
                                           connection = connection)
        put_frame_pretty_name(connection._meta_kb,'All Local Knowledge',
                              kb=connection._meta_kb)
        connection._meta_kb._add_frame_to_store(Node._primordial_kb)
        from PyKb import PyKb
        connection._default_kb_type = PyKb
        connection._ignore_tildes = 1


    def _find_kbs_in(connection,place):
        ignore_dirs = ['CVS','.bzr']
        ignore_things_starting_with = ['#']
        rets = []
        entries = dircache.listdir(place)        
        for e in entries:
            #print "considering e =",e
            splits = os.path.splitext(e)

            if not (connection._ignore_tildes and e[-1] == '~') \
                    and not (e in ignore_dirs) \
                    and not (e[0] in ignore_things_starting_with) \
                    or os.path.isdir(os.path.join(place,e)):
                
                if splits[-1] in pyokbc_mimetypes.keys():
                    just_the_name = string.join(list(splits[:-1]),'')
                    rets.append(just_the_name)
                else:
                    rets.append(e)
        return rets

    @timed
    def openable_kbs(connection,kb_type,place=None):
        if not place: place = connection._default_place
        #warn("openable_kbs doing listdir of "+place)

        rets = ['PRIMORDIAL_KB']
        for place in connection._path:
            rets.extend(connection._find_kbs_in(place))

        rets.sort()
        return rets

    def get_full_path(connection,filename):
        return _make_allowed_fname(connection._path[0],filename)

    def _lines_and_stats(connection,filename,place):
        path = connection._path
        #print "_lines_and_stats place =",place,filename
        if place != '':
            path = [place]
        lines = []
        for a_place in path:
            if __builtins__.has_key('nooron_root'): # FIXME bad hack
                fname = _make_allowed_fname(a_place,filename)
            else:
                fname = os.path.join(place,filename)
            try:
                f = open(fname)
                #print "found",fname
                #raise bogusissue
                lines = f.readlines()
                f.close()
                break
            except:
                print "failing to find",fname
                continue
        if lines:
            stats = connection._stats(fname)
            return (lines,stats)
        else:
            raise KbNotFound,(filename,path)            

    def _stats(connection,fname):
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
        return stats

    def __str__(self):
        """
        return results like "/home/smurp/knowledge/{one,two,three}"
        """
        common = os.path.commonprefix(self._path)
        if len(self._path) > 1:
            return common + '{' + ','.join([p[len(common):] for p in self._path]) + '}'
        elif len(self._path) == 1:
            return self._path[0]
        else:
            return None
