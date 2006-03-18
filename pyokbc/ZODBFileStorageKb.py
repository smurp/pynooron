
from PyOkbc import *
#from OkbcConditions import *
from CachingMixin import CachingMixin

from ZODB.DB import DB
from ZODB.FileStorage import FileStorage
import transaction
import logging

"""
This is the implementation of ZodbKb for files with the extension .zfskb

----------------------------------------------------------------

A fair discussion here is whether a ZodbKb should be stored in a single ZODB .fs
file of its own or whether a .fs file should have a connection established to
it and multiple Kbs should live within one.

What are the issues?
1) Locking happens on a per-file basis with ZODB.FileStorage
2) If there is one kb per file then they can be moved around more easily
   WRT to one another.
3) Basically, the question is "why tie kbs together in a single file?"
   i) performance? unclear how important this is
   ii) discovery?  in-zodb indices of which kbs are available 
   iii) metadata?  natural place for metadata about kbs, within the file

Conclusion:
  One-kb-per-file makes administrative and configuration operations simpler.
  Perhaps a MetaKb.zfskb per-directory could aid discovery.
"""

import os
from DictOnDict import DictOnDict

class ZfsKb(AbstractFileKb #,CachingMixin
            ):
    _kb_type_file_extension = 'zfskb'
    make_backups = 0
    via_temp = 0
    def open_kb(self,kb_locator,connection=None,error_p=1):
        pass
    def create_kb(self,name,kb_locator=None,initargs={},connection=None):
        pass
                  

    def __init__(self,kb_locator,connection,name=None,initargs={},error_p=1):
        """
        We do the bare minimum of work here, because this is just a preface
        to doing either open_kb or create_kb.

        This is very weird.  This method accepts the spanning set of args to
        open_kb and create_kb and can be called as either.  It should try
        to figure out which method it is being called as so it can figure
        out which sorts of errors to raise -- in particular:
          iff called_as == open_kb then raise KbNotFound
          iff called_as == create_kb then raise KbCanNotCreate
        
        open-kb     ( kb-locator &key kb-type (connection (local-connection)) (error-p true))
        create-kb     ( name &key kb-type kb-locator initargs (connection (local-connection))) 
        """
        metakb = connection.meta_kb()

        if name==None:
            called_as = 'open_kb'
        else:
            called_as = 'create_kb'
        print called_as
        if type(kb_locator) == type(''):
            ext = self._kb_type_file_extension
            if not (len(kb_locator) > len(ext) and \
                    kb_locator[-1 * len(ext):] == ext):
                filename = kb_locator + '.' + ext
            else:
                filename = kb_locator
            if name==None:
                name = kb_locator # should really get the basename w/o ext
        elif type(kb_locator) == type({}):
            filename = kb_locator['db-file']
            if name==None:
                name = kb_locator['name']
        elif metakb.instance_of_p(kb_locator,':KB_LOCATOR')[0]:
            filename = metakb.get_slot_value(kb_locator,'filename')[0]
        else:
            filename = name + '.' + self._kb_type_file_extension
            #print 'WHAT_THE?',type(kb_locator),kb_locator,name
        fullpath = connection.get_full_path(filename)

        self._fullpath = fullpath
        self._name = name
        self._filename = filename
        self._place = ''

        AbstractFileKb.__init__(self,name,connection=connection)
        #CachingMixin.__init__(self)

        filestore = FileStorage(self._fullpath)
        database = DB(filestore)
        self._v_database = database
        self._open_zodb_database()
        self._v_deletes = []
        self._v_store = DictOnDict(self._v_conn.root(),
                                   restore_frame = self._restore_frame_from_storage,
                                   restore_kb = self
                                   )
        
        #self._v_store = \
        #    DictOnDict(inner_dict = self._v_conn.root(),
        #               list_of_deletes = self._v_deletes
        #               )

        prev_kb = current_kb()
        goto_kb(self)

        #orig_allow_caching_p = self.allow_caching_p()
        #self._allow_caching_p = 0
        self._changes_register_as_modifications_p = 0
        stats = connection._stats(filename)
#        for (key,val) in stats.items():
#            self.put_slot_value(self,str(key),val)
        
        #return self._changes_register_as_modifications_p        
        self._changes_register_as_modifications_p = 1
        #print "setting changes_register... ",self.changes_register_as_modifications_p(),"in",self
        #self._allow_caching_p = orig_allow_caching_p
        goto_kb(prev_kb)

    def _open_zodb_database(self):
        self._v_conn = DB.open(self._v_database)

    def _save_frame(kb,frame):  # DEPRECATED
        from pickle import dumps
        root = kb._v_store
        #root = kb.conn.root()
        #print dir(pp)
        if 0:
            for k in frame.__dict__.keys():
                try:
                    dumps(frame[k])
                except:
                    print "problem in",k
                    raise

        root[kb.get_frame_name(frame)] = frame
            
        #print "ZfsKb._save_frame not implemented"

    def _save_frame_to_storage(kb,frame,stream=1):
        root = kb._v_store
        frame_name = kb.get_frame_name(frame)
        #print "saving",frame_name,"explicitly"

        args_and_kwargs = frame._return_as_args_and_kwargs()
        #print args_and_kwargs # pymeth(*args, **kwds)
        #([])
        root[frame_name] = args_and_kwargs

    def _restore_frame_from_storage(kb,frame_name):
        if root.has_key(frame_name):
            (args, kwargs) = root[frame_name]
            frame = apply(kb.create_frame,args,kwargs)
            return frame

    def _propagate_deletions_to_base_dict(self):
        base_dict = self._v_store.get_base_dict()
        for key in self._v_store.get_deleted_keys():
            try:
                del base_dict[key]
            except:
                print "%s deleted, though not in base_dict" % key
            
    def _cause_frames_to_persist(self):
        #print "persisting"
        self._propagate_deletions_to_base_dict()
        base_dict = self._v_store.get_base_dict()
        for frame_name,frame in self._v_store.get_cached_items():
            args_and_kwargs = frame._return_as_args_and_kwargs()
            #print args_and_kwargs 
            base_dict[frame_name] = args_and_kwargs
        #print "/persisting"            

    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0,
                                 checked_kbs=None):
        if kb._v_store.has_key(thing):
            #print 'found thing:',thing
            return (kb._v_store.get(thing),1)
        return (None,None)

    def _open_output_file_at_path(kb,path):
        pass

    def _begin_transaction(kb):
        #kb._v_conn.transaction_manager.free(kb._v_conn.transaction_manager.get())
        #print 'begin  ',kb._v_conn,kb._v_conn.transaction_manager#,kb._v_conn.transaction_manager._txn

        kb._open_zodb_database()
        #print 'begin'
        kb._v_conn.transaction_manager.begin()        
        #transaction.begin()
        #print '/begin'        

    def _commit_transaction(kb):
        #print 'commit ',kb._v_conn,kb._v_conn.transaction_manager
        #print 'commit'
        kb._v_conn.transaction_manager.commit()        
        #transaction.commit()
        #print '/commit'

    def _close_output_file(kb):
        kb._close_kb()

    def close_kb_internal(kb,save_p = 0):
        meta = kb.connection().meta_kb()
        if save_p:
            kb.save_kb()
        else:
            kb._v_conn.transaction_manager.abort()
        meta.delete_frame(kb)
        kb._close_kb()

    def _close_kb(kb):
        kb._v_conn.close()

    def _write_preamble(kb):
        pass

    def _write_kb_own_attributes(kb):
        pass
    
