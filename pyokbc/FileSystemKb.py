
"""FileSystemKB presents a directory (and its subdirectories) as a KB."""
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: FileSystemKb.py,v 1.2 2002/11/26 21:52:40 smurp Exp $'

import string

from PyOkbc import *
import string
import os
import mimetypes
#import dircache

from PyKb import *
from TellKb import *

pyokbc_mimetype_file = os.path.join(os.path.dirname(__file__),'mime.types')
mimetypes.init([pyokbc_mimetype_file])
pyokbc_mimetypes = mimetypes.read_mime_types(pyokbc_mimetype_file)

class FileSystemKb(AbstractFileKb):
    #_mimetypes = mimetypes.read_mime_types(pyokbc_mimetype_file)
    def __init__(kb,filename,place='',connection=None):
        #print kb._mimetypes
        AbstractFileKb.__init__(kb,filename,connection=connection)
        kb._kb_types = {'application/vnd.pyokbc.kb.pykb':PyKb,
                        'application/vnd.pyokbc.kb.tell':TellKb,
                        }

    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0):
        conn = kb._connection
        frame_found_p = 1
        frame = kb._cache.get(str(thing))
        #print "looking in",str(kb),"for",thing,
        if frame:
            #print 'found'
            return (frame,1)
        
        if thing.find('__') > -1:
            possible_mime_type = thing.replace('__','/')
            if possible_mime_type in mimetypes.types_map.values():
                #print "found"
                frame = kb.create_frame(thing,Node._individual,
                                        pretty_name = possible_mime_type,
                                        direct_types=['mimetype'])
                return (frame,1)

        if thing in os.listdir(str(kb)):
            #print "found '%s' on disk" % thing
            direct_types = []
            (mime_type,encoding) = mimetypes.guess_type(thing)
            if mime_type:
                mime_type = mime_type.replace('/','__')
                direct_types.append(mime_type)
            file_contents = conn._obtain_raw_file(thing,
                                                  place=str(kb))
            frame = kb.create_frame(thing,Node._individual,
                                    direct_types=direct_types,
                                    own_slots=[['file_contents',
                                                file_contents]])

            return (frame,1)

        for (ext,mime_type) in pyokbc_mimetypes.items():
            #possible_kb_filename = os.path.join(str(kb),filename+ext)
            possible_kb_filename = thing + ext
            if possible_kb_filename in os.listdir(str(kb)):
                kb_type = kb._kb_types.get(mime_type)
                if kb_type:
                    #print 'found'
                    frame = kb_type(possible_kb_filename,
                                    connection = kb._connection,
                                    name = thing)
                    #print "caching",frame
                    kb._add_frame_to_cache(frame)

                    return (frame,1)

        #print 'not found'
        return (None,None)













