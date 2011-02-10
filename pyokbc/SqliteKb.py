#!/usr/bin/env python

"""
There are several ways to go wrt the use of sqlite for kb storage.
1) have multiple kbs in one sqlite db and make it a connection
2) have one kb in an sqlite db and find them using FileSystemConnection

>>> str(local_connection())
"SqliteConnection(initargs={'place':':memory'})"
>>> set(openable_kbs(SqliteKb))
set([u'PRIMORDIAL_KB'])
>>> test_kb = create_kb('TestKB')
>>> set(openable_kbs(SqliteKb))
set([u'PRIMORDIAL_KB',u'TestKB'])
>>> create_class('TestKB','Person',doc='homo habilis and up',pretty_name="")
>>> put_slot_value('TestKB','TheAnswer','hasValue',42)
>>> get_slot_value('TestKB','TheAnswer','hasValue')[0]
[42]
>>> sql_get_many(local_connection().conn,"select * from kb_frame_slot_values;")
'onk'
>>> local_connection().dump()
adsf
"""

import sys
sys.path.append("..")
from PyOkbc import *
from sql_convenience_functions import *
import sqlite3
from debug_tools import timed
        
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SqliteConnection(Connection):
    default_initargs = {'place':':memory'}
    def __init__(connection,initargs={}):
        if initargs == None:
            initargs = connection.default_initargs
        if not initargs.has_key('place'):
            initargs.update(connection.default_initargs)

        connection.place = initargs['place']
        connection.conn = sqlite3.connect(connection.place)
        #connection.conn.row_factory = dict_factory
        connection.conn.row_factory = sqlite3.Row
        connection._initargs = initargs

        if not connection._is_initialized():
            connection._initialize()
        if globals().get('LOCAL_CONNECTION',None) == None:
            global LOCAL_CONNECTION
            LOCAL_CONNECTION = connection


        name = SqliteMetaKb.name
        connection._meta_kb = SqliteMetaKb(name,name=name,connection=connection)
        connection._default_kb_type = SqliteKb

    def __del__(self):
        sql_execute(self.conn,"commit;")
    
    def __str__(self):
        return "%s(initargs={'place':'%s'})" % (self.__class__.__name__,
                                                self._initargs['place'])
    def meta_kb(conn):
        return conn._meta_kb

    def dump(self):
        return sql_dump(self.conn.cursor(),"select * from kb_frame_slot_values")

    def _is_initialized(conn):
        try:
            res = sql_get_many(conn.conn.cursor(),
                               "select count(*) from kb_frame_slot_values")
            return True
        except Exception,e:
            if str(e).count("no such table"):
                return False
            else:
                raise
        
    def _initialize(conn):
        create_sql = """
          create table kb_frame_slot_values (
            kb             varchar,
            frame          varchar,
            slot           varchar,
            value_order    int, -- -1 for single-valued or set-valued slots, otherwise 0 thru n for lists
            value_type     char(5), -- str,int,date,float to indicate which value_????
            value_str      varchar,
            value_int      integer,
            value_date     datetime,
            value_float    float,
            creator        varchar,
            creation_time  timestamp,
            modifier       varchar,
            modification_time timestamp,
            primary key (kb,frame,slot,value_order)
          );
        """
        sql_execute(conn.conn.cursor(),create_sql)

    @timed
    def find_kb_locator(connection,thing,kb_type=None):
        meta = connection.meta_kb()
        frame,frame_found_p = meta.get_frame_in_kb(thing)
        msg = "frame=%s frame_found_p=%s" % (frame,frame_found_p)
        raise ValueError(msg)
        if frame_found_p:
            git = "get_instance_types(%s)" % frame
            if meta.instance_of_p(frame,':kb_locator'):
                #meta.print_frame(frame)
                return frame
            else:
                pass
        return connection.create_kb_locator(thing,kb_type=kb_type)

    def openable_kbs(conn,kb_type,place=None):
        return conn.meta_kb().get_slot_values(SqliteMetaKb.name,
                                              'isKbOfType')[0] + [u'PRIMORDIAL_KB']
        return sql_get_column(
                conn.conn.cursor(),
                """select 'PRIMORDIAL_KB' 
                   UNION 
                   select frame 
                   from kb_frame_slot_values 
                   where kb=? and 
                         slot='isKbOfType' 
                         and value_order = 0""",
                (SqliteMetaKb.name,))
        return rets


class SqliteKb(AbstractFileKb):
    """There are several ways to go with this."""
    _type_slot_name = "_isFrameOfType" # :SLOT,:INDIVIDUAL,:CLASS,:FACET [,:KB](?)

    def __init__(self,filename_or_kb_locator,
                 place="",
                 connection = None, name = None,
                 initargs = {}):
        self._connection = connection
        metakb = self._get_meta_kb()
        name = filename_or_kb_locator
        assert(name != None,"name should not equal '%s'" % name)
        node_kb = Node.__dict__.get('_kb')
        FRAME.__init__(self,name,frame_type=node_kb,kb=metakb)
        self.kb_locator = filename_or_kb_locator
        self._name = name
        self.initargs = initargs
        self._the_parent_kbs = []

    def _get_meta_kb(self):
        return self._connection.meta_kb()

    def _cursor(kb):
        return kb._connection.conn.cursor()

    @timed
    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0):
        sql = """select value_str from kb_frame_slot_values 
                 where kb=? and frame=? and slot=?"""
        found_frame = None
        frame_type_name = sql_get_one(kb._cursor(),
                                      sql,
                                      (str(kb),str(thing),kb._type_slot_name))
        #print "frame_type_name",frame_type_name
        assert(frame_type_name <> None,
               "frame_type_name should not be '%s'" % frame_type_name)
        if frame_type_name <> None:
            found_frame = globals()[frame_type_name](str(thing))

        if found_frame == None:
            if thing == kb or str(thing) == str(kb):
                found_frame = kb
        # FIXME the whole coercibility issue is ignored
        if found_frame:
            return (found_frame,found_frame != None)
        else:
            return (None,None)

    def get_slot_values_in_detail_internal(
        kb,frame,slot,
        inference_level = Node._taxonomic,
        slot_type = Node._own,
        number_of_values = Node._all,
        value_selector = Node._either,
        kb_local_only_p = 0,
        checked_kbs=[],checked_classes=[]):

        (list_of_specs,exact_p,more_status,default_p) = ([],1,0,0)
        frame = kb.coerce_to_frame_internal(str(frame))
        if frame == None:
            return [[],1,0,1]
        raw_slot_values = sql_get_many(
            kb._cursor(),
            """select *
               from kb_frame_slot_values 
               where kb=? 
                     and frame=?
                     and slot=? 
               order by value_order""",
            params = (SqliteMetaKb.name,str(frame),str(slot)))
        for rsv in raw_slot_values:
            list_of_specs.append([rsv[str('value_'+rsv['value_type'])],1,0])
        return (list_of_specs,exact_p,more_status,default_p)


    
    def BOGUS_add_frame_to_store(self,frame):
        sql = """
        insert into kb_frame_slot_values 
           (kb,frame,slot,value_type,value_order,value_str) values 
           (?, ?,    ?,   'str',   0,          ?        )
        """ % ()
    
    @timed
    def _add_frame_to_store(kb,frame):
        sql = """
        insert into kb_frame_slot_values 
           (kb,frame,slot,value_type,value_order,value_str) values 
           (?, ?,    ?,   'str',   0,          ?        )
        """
        try:
            frame_name = str(frame)
        except:
            frame_name = frame._name
        curs = sql_execute(kb._cursor(),
                           sql, 
                           (kb.name,
                            frame_name,
                            'isKbOfType',
                            str(kb.__class__.__name__)))
        return curs

class SqliteMetaKb(SqliteKb):
    name = "DefaultMetaKb"

    def coerce_to_frame_internal(kb,frame):
        sql = """select count(*) from kb_frame_slot_values 
                 where kb=? and frame=?"""
        if sql_get_one(kb._cursor(),sql,
                       (str(kb),str(frame))):
            return frame
        return None

    def _get_meta_kb(self):
        return self
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
