#!/bin/env python

"""FileSystemKB presents a directory (and its subdirectories) as a KB."""
__version__='$Revision: 1.17 $'[11:-2]
__cvs_id__ ='$Id: FileSystemKb.py,v 1.17 2008/08/13 16:08:47 smurp Exp $'

import string

from debug_tools import timed
from PyOkbc import *
import string
import os
import mimetypes
#import dircache

from PyKb import *
from TellKb import *
from BrainKb import *
import sys


python_version = sys.version.split(' ')[0]
pyokbc_mimetype_file = os.path.join(os.path.dirname(__file__),'mime.types')
mimetypes.init([pyokbc_mimetype_file])
pyokbc_mimetypes = mimetypes.read_mime_types(pyokbc_mimetype_file)

class FileSystemKb(AbstractFileKb):
    #_mimetypes = mimetypes.read_mime_types(pyokbc_mimetype_file)
    def __init__(kb,filename,place='',connection=None):
        #print kb._mimetypes
        kb._typed_cache = {}
        AbstractFileKb.__init__(kb,filename,connection=connection)
        kb._kb_types = {'application/vnd.pyokbc.kb.pykb':PyKb,
                        'application/vnd.pyokbc.kb.tell':TellKb,
                        'application/vnd.brain':BrainKb,
                        }
        try:
            kb._kb_types['application/vnd.pyokbc.kb.zfskb'] = ZfsKb
        except:
            pass
        kb._make_kb_types_by_extension()

    def _make_kb_types_by_extension(kb):
        kb._kb_types_by_extension = ktbe = {}
        for kb_type in kb._kb_types.values():
            ktbe[kb_type._kb_type_file_extension] = kb_type

    @timed
    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0):
        conn = kb._connection
        frame_found_p = 1
        frame = kb._v_store.get(str(thing))
        #print "looking in",str(kb),"for",thing,
        if frame:
            #print 'found'
            return (frame,1)

        if thing == kb:
            return (thing,1)
        
        if type(thing) == type('') and thing.find('__') > -1:
            possible_mime_type = thing.replace('__','/')
            if possible_mime_type in mimetypes.types_map.values():
                #print "found"
                frame = kb.create_frame(thing,Node._individual,
                                        pretty_name = possible_mime_type,
                                        direct_types=['mimetype'])
                return (frame,1)

        for place in kb._connection._path:
            #print "seeking %s in %s"%(thing,place)
            if thing in os.listdir(place):
                #print "found '%s' on disk" % thing
                direct_types = []
                (mime_type,encoding) = mimetypes.guess_type(thing)
                if mime_type:
                    mime_type = mime_type.replace('/','__')
                    direct_types.append(mime_type)
                (file_contents,stats) = conn._lines_and_stats(thing,
                                                              place=place)
                own_slots = [['file_contents',file_contents]]
                for (key,val) in stats.items():
                    own_slots.append([key,val])

                frame = kb.create_frame(thing,Node._individual,
                                        direct_types=direct_types,
                                        own_slots=own_slots)

                return (frame,1)

            for (ext,mime_type) in pyokbc_mimetypes.items():
                #possible_kb_filename = os.path.join(place,filename+ext)

                #print "thing =",str(thing),type(thing),type(ext)
                possible_kb_filename = thing + ext
                if possible_kb_filename in os.listdir(place):
                    kb_type = kb._kb_types.get(mime_type)
                    if kb_type:
                        #print kb_type,possible_kb_filename,kb._connection,thing


                        poss_path = string.split(possible_kb_filename,'/')
                        #print "poss_path =",poss_path
                        if len(poss_path) > 1:
                            place = os.path.join(place,poss_path[0:-2])
                            possible_kb_filename = poss_path[-1]
                            #print "place = %s  filename = %s" % (place,
                            #                                    possible_kb_filename)


                            
                        frame = kb_type(possible_kb_filename,
                                        connection = kb._connection,
                                        place = place,
                                        name = thing)
                        #print "caching",frame
                        kb._add_frame_to_store(frame)

                        return (frame,1)

        #print 'not found'
        return (None,None)














