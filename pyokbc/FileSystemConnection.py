
__version__='$Revision: 1.23 $'[11:-2]
__cvs_id__ ='$Id: FileSystemConnection.py,v 1.23 2008/08/13 16:08:47 smurp Exp $'

from PyOkbc import *
from OkbcConditions import *
#import dircache
import os
from FileSystemKb import *
import string

def _make_allowed_fname(allowed_place,kb_locator):
    #if DEBUG: print "make_fname",frag
    #print "_make_allowed_fname",allowed_place,kb_locator
    #print allowed_place,kb_locator
    fullpath = os.path.join(allowed_place,kb_locator)
    normpath = os.path.normpath(fullpath)
    if string.find(kb_locator,'nooron_app') == 0:
        print "LOOKING FOR nooron_app IN",allowed_place,normpath
        
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
        put_frame_pretty_name(connection._meta_kb,'All Local Knowledge',
                              kb=connection._meta_kb)
        connection._meta_kb._add_frame_to_store(Node._primordial_kb)
        from PyKb import PyKb
        connection._default_kb_type = initargs.get('default_kb_type',PyKb)
        connection._ignore_tildes = initargs.get('ignore_tildes',True)

    def find_kb_locator(connection,thing,kb_type=None):
        meta = connection.meta_kb()
        if not meta._v_store.has_key(str(thing)):
            #print meta._v_store.keys()
            #import pdb; pdb.set_trace()
            return connection.create_kb_locator(thing,kb_type=kb_type)
        return meta.get_frame_in_kb(thing)[0]

    def create_kb_locator(connection,
                          thing,
                          kb_type = None):
        """Create a frame in the meta_kb for the kb 'thing'.

        Thing may or may not have an extension.  If it lacks an extension
        then it will be given an extension suitable for the kb_type.
        If kb_type is not given and thing has no extension then an inspection
        of the filesystem will occur looking for files with known extensions
        which have a basename as in 'thing'.  If no such file is found kb_type
        will be set to the default kb_type for this connection.
        
        @param kb_type a subclass of AbstractFileKb.
        
        """
        thing_has_extension = len(thing.split('.')) > 1
        extension = thing_has_extension and thing.split('.')[-1] or None
        file_name = thing_has_extension and thing or None
        
        if kb_type and extension <> None and \
               kb_type._kb_type_file_extension <> extension:
            #print kb_type
            #print extension
            raise('KBTypeAndExtensionMismatch_%s_<>_%s' % (
                kb_type._kb_type_file_extension,
                extension))
        files = connection._find_kbs_in(connection._default_place)

        # if the extension is determined, constrain to it now
        if kb_type and not extension:
            extension = kb_type._kb_type_file_extension
            file_name = thing + '.' + extension

        metakb = connection.meta_kb()
        ktbe = metakb._kb_types_by_extension
        #print "looking for",thing
        if not extension:
            for f in files:
                if f.startswith(thing):

                    if len(f.split('.')) > 1:
                        possible_extension = f.split('.')[-1]
                        print f,'starts with',thing,possible_extension
                        if ktbe.has_key(possible_extension):
                            extension = possible_extension
                            file_name = f
                            kb_type = ktbe.get(extension)
                            break
            else: # thing was not found
                #print "using default_kb_type"
                kb_type = connection._default_kb_type
                file_name = thing + '.' + kb_type._kb_type_file_extension

        if extension and not kb_type:
            print ktbe
            print extension
            kb_type = ktbe.get(extension)

        #print "we are getting to here",kb_type,thing,file_name
        #return kb_type(thing,connection=connection)
        just_name = thing.split('.')[0]
        #print "create_kb_locator(name=%s,file=%s)" % (thing,file_name)
        locator = {'file_uri':file_name,'kb_name':just_name}
        return kb_type(locator,connection=connection)
        return kb_type(file_name,connection=connection)
    
        fr = metakb.create_individual(thing,#just_name, #thing,#file_name,
                                      direct_types = [':kb_locator'],
                                      own_slots = [[':KB_TYPE',kb_type],
                                                   ['filename',file_name]])

        return fr
        
    def open_kb_internal(connection, name_or_kb_locator,kb_type = None,
                         errro_p = 1):
        pass
            
    def _find_kbs_in(connection,place):
        rets = []
        entries = []
        for dir in place.split(':'):
            print "",dir
            more = os.listdir(dir)
            #for file in more:
            #    print "  ", file
            entries.extend(more)

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
        my_meta_kb = connection.meta_kb()
        
        if not place: place = connection._default_place
        warn("openable_kbs doing listdir of "+place)

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
            #if __builtins__.has_key('nooron_root'): # FIXME bad hack
            #    fname = _make_allowed_fname(a_place,filename)
            #else:
            fname = os.path.join(a_place,filename)
            try:
                f = open(fname)
                #print "ahh, found", fname,"in",a_place
                #print "found",fname
                #raise bogusissue
                lines = f.readlines()
                f.close()

                break
            except Exception,e:
                #print "failing to find",fname,"in",a_place
                #print e
                continue
        if lines:
            stats = connection._stats(fname)
            return (lines,stats)
        else:
            raise KbNotFound,(filename,path,)

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
