#!/usr/bin/env python

"""
There are several ways to go wrt the use of sqlite for kb storage.
1) have multiple kbs in one sqlite db and make it a connection
2) have one kb in an sqlite db and find them using FileSystemConnection

>>> str(local_connection())
"SqliteConnection(initargs={'place':':memory:'})"
>>> set(openable_kbs(SqliteKb)) == set([u'DefaultMetaKb', u'PRIMORDIAL_KB'])
True
>>> test_kb = create_kb('TestKB')
>>> set(openable_kbs(SqliteKb)) == set([u'TestKB', u'DefaultMetaKb', u'PRIMORDIAL_KB'])
True
>>> goto_kb(test_kb)
>>> put_slot_value('TheAnswer','hasValue',42)
>>> get_slot_value('TheAnswer','hasValue')[0]
42
>>> local_connection().dump()
                  kb |                frame |  slot_type |                 slot | order |  type | value
-------------------- | -------------------- | ---------- | -------------------- | ----- | ----- | ---------------
       DefaultMetaKb |        DefaultMetaKb |       :own |             isOfType |     0 |   str | SqliteMetaKb
       DefaultMetaKb |               TestKB |       :own |             isOfType |     0 |   str | SqliteKb
              TestKB |            TheAnswer |       :own |             hasValue |     0 |   int | 42

>>> DoC = create_individual('DeckOfCards',own_slots=[['hasSuits','Clubs','Hearts','Diamonds','Spades']])
>>> set(get_slot_values('DeckOfCards','hasSuits')[0]) == set(u'Clubs Hearts Diamonds Spades'.split(' '))
True
>>> person = create_class('Person',template_slots=[['eatsFoods','Fruit','Vegetables','Meat']],doc="homo habilis and up")

#>>> alice = create_individual('Alice',direct_types = ['Person'], own_slots=[['eatsFoods','Potions']])
#>>> set(get_slot_values('Alice','eatsFoods')[0]) # == set(u'Fruit Vegetables Meat Potions'.split(' '))
#True
"""

import sys
sys.path.append("..")
from PyOkbc import *
from sql_convenience_functions import *
import sqlite3
from debug_tools import timed

def get_value_type(value):
    """
    >>> import datetime
    >>> get_value_type(23)
    'int'
    >>> get_value_type(12.3)
    'float'
    >>> get_value_type(datetime.datetime(1925,12,25,10,10,30))
    'date'
    >>> get_value_type(datetime.date(1925,12,25))
    'date'
    >>> get_value_type('boo')
    'str'
    >>> get_value_type(None) # random thing
    'str'
    >>> get_value_type(ValueError('boo')) # random thing
    'str'
    """
    import datetime
    typ_map = {int:'int',float:'float',str:'str',datetime.datetime:'date',datetime.date:'date'}
    value_type = typ_map.get(type(value),'str')
    return value_type
        
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def simplify_row(dct):
    dct = dict(dct)
    dct['value'] = dct['value_'+dct['value_type']]
    return dct

class SqliteConnection(Connection):
    default_initargs = {'place':':memory:'}
    def __init__(connection,initargs={}):
        if initargs == None:
            initargs = connection.default_initargs
        if not initargs.has_key('place'):
            initargs.update(connection.default_initargs)

        connection.place = initargs['place']
        connection.conn = sqlite3.connect(connection.place,isolation_level=None)
        #connection.conn.row_factory = dict_factory
        connection.conn.row_factory = sqlite3.Row
        connection._initargs = initargs

        if not connection._is_initialized():
            connection._initialize()
        if globals().get('LOCAL_CONNECTION',None) == None:
            global LOCAL_CONNECTION
            LOCAL_CONNECTION = connection
        #sql_execute(connection.conn,"begin transaction;")

        name = SqliteMetaKb._name
        connection._meta_kb = SqliteMetaKb(name,name=name,connection=connection)
        connection._default_kb_type = SqliteKb

    def __del__(self):
        #sql_execute(self.conn.cursor(),"commit;")
        1

    def __str__(self):
        return "%s(initargs={'place':'%s'})" % (self.__class__.__name__,
                                                self._initargs['place'])
    def meta_kb(conn):
        return conn._meta_kb

    def dump(self,**kwargs):
        tmpl = "%(kb)20s | %(frame)20s | %(slot_type)10s | %(slot)20s | %(value_order)5s | %(value_type)5s | %(value)s" 
        header_printed = False
        sql = "select * from kb_frame_slot_values"
        params = []
        for field,value in kwargs.items():
            if not locals().has_key('where_added'):
                sql += ' where '
                where_added = True
            sql += ' %s=? ' % field
            params.append(value)
        for row in sql_get_many(self.conn.cursor(),sql,params):
            if not header_printed:
                header_printed = True
                print tmpl % dict(kb='kb',frame='frame', slot_type="slot_type", slot='slot', value_type="type",
                                  value_order='order', value = 'value')
                print tmpl % dict(kb='-'*20,frame='-'*20, slot_type='-'*10, slot='-'*20, value_type="-"*5,
                                  value_order='-'*5, value='-'*15)
            simple_row = simplify_row(row)
            print tmpl % simple_row
        

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
        
    @timed
    def _initialize(conn):
        create_sql = """
          create table kb_frame_slot_values (
            kb             varchar,
            frame          varchar,
            slot_type      varchar,
            slot           varchar,
            value_order    int default 0, -- 0 thru n for lists
            value_type     char(5), -- str,int,date,float to indicate which value_????
            value_str      varchar,
            value_int      integer,
            value_date     datetime,
            value_float    float,
            creator        varchar,
            creation_time  timestamp,
            modifier       varchar,
            modification_time timestamp
            ,primary key (kb,frame,slot_type,slot,value_order)
          );
        """
        sql_execute(conn.conn.cursor(),create_sql)
        return create_sql

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
        #return conn.meta_kb().get_slot_values(SqliteMetaKb._name,
        #                                      'isOfType')[0] + [u'PRIMORDIAL_KB']
        return sql_get_column(
                conn.conn.cursor(),
                """select 'PRIMORDIAL_KB' 
                   UNION 
                   select frame 
                   from kb_frame_slot_values 
                   where kb=? and 
                         slot='isOfType' 
                         and value_order = 0""",
                (SqliteMetaKb._name,))
        return rets


class SqliteKb(TupleKb):
#class SqliteKb(AbstractFileKb):
    """There are several ways to go with this."""
    _type_slot_name = "_isFrameOfType" # :SLOT,:INDIVIDUAL,:CLASS,:FACET [,:KB](?)

    def __init__(self,filename_or_kb_locator,
                 place="",
                 connection = None, name = None,
                 initargs = {}):
        self._connection = connection
        metakb = self._get_meta_kb()
        name = filename_or_kb_locator or name
        self._name = name
        node_kb = Node.__dict__.get('_kb')
        FRAME.__init__(self,name,frame_type=node_kb,kb=metakb)
        self.kb_locator = filename_or_kb_locator
        self.initargs = initargs
        self._the_parent_kbs = []

    def _get_meta_kb(self):
        return self._connection.meta_kb()

    def _cursor(kb):
        return kb._connection.conn.cursor()


    @timed
    def _get_frame_type(kb,thing):
        sql = """select value_str from kb_frame_slot_values 
                 where kb='%s' and frame='%s' and slot='%s'"""
        args = (str(kb),str(thing),kb._type_slot_name)
        sql = sql % args
        frame_type_name = sql_get_one(kb._cursor(),
                                      sql)
        try:
            return locals()[frame_type_name]
        except KeyError,e:
            raise(KeyError("No class named '%s' found. using query %s" % (
                        frame_type_name, sql)))
        

    @timed
    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0):
        try:
            frame_type = kb._get_frame_type(thing)
        except KeyError,e:
            return (None,None)
        found_frame = frame_type(str(thing))

        if found_frame == None:
            if thing == kb or str(thing) == str(kb):
                found_frame = kb
        # FIXME the whole coercibility issue is ignored
        if found_frame:
            return (found_frame,found_frame != None)
        else:
            return (None,None)

    @timed
    def get_slot_values_in_detail_internal(
        kb,frame,slot,
        inference_level = Node._taxonomic,
        slot_type = Node._own,
        number_of_values = Node._all,
        value_selector = Node._either,
        kb_local_only_p = 0,
        checked_kbs=[],checked_classes=[]):

        #raise(ValueError([type(slot),slot]))
        (list_of_specs,exact_p,more_status,default_p) = ([],1,0,0)
        frame = kb.coerce_to_frame_internal(str(frame))
        if frame == None:
            return [[],1,0,1]
        params = (str(kb),str(frame),str(slot))
        sql = """select *
               from kb_frame_slot_values 
               where kb='%s'
                     and frame='%s'
                     and slot='%s'
               order by value_order""" % params
        #raise(ValueError(sql))
        raw_slot_values = sql_get_many(
            kb._cursor(),
            sql)

        for rsv in raw_slot_values:
            list_of_specs.append([rsv[str('value_'+rsv['value_type'])],1,0])
        return (list_of_specs,exact_p,more_status,default_p)

    def put_slot_value_internal(kb,frame_name,slot, value,
                                slot_type=Node._own,
                                value_selector = Node._known_true,
                                kb_local_only_p = 0):
        """Sets the values of slot in frame to be a singleton set
        consisting of a single element: value.  This operation may
        signal constraint violation conditions (see Section 3.8).
        Returns no values. """
        #if str(slot) == 'ModificationTime':      ## REMOVE
        #    warn('get_class_subclasses ignores inference_level > direct')
        if type(value) == type([]): raise CardinalityViolation,str(value)
        (frame,frame_found_p) = kb.get_frame_in_kb(frame_name)
        slot_key = str(slot)
        (slot,slot_found_p) = kb.get_frame_in_kb(slot)
        #if not slot_found_p and str(
        if True:
            # FIXME NO DISTINCTION BETWEEN own and template
            sql = "select count(*) as cnt from kb_frame_slot_values where kb=? and frame=? and slot=?"
            prm = (str(kb),str(frame_name),str(slot))
            count = sql_get_one(kb._cursor(),sql,prm)['cnt']
            if count == 1:
                sql = "update kb_frame_slot_values set "
            elif count > 1:
                raise ValueError("Too many values for put_slot_values_internal COUNT:%s SQL:%s" %(sql,count))
            else: # no records
                value_type = get_value_type(value)
                # FIXME value_type 'date' not handled
                sql = str("insert into kb_frame_slot_values " + \
                              "(kb,frame,slot_type,slot,value_%s,value_type,value_order) " +\
                              "values (?,?,?,?,?,'%s',0)") % (
                    value_type,value_type)
                prm = (str(kb),str(frame_name),str(slot_type),str(slot_key),value)
                curs = sql_execute(kb._cursor(),sql,prm)

        #if slot_type == Node._own:           pass
        #elif slot_type == Node._template:    pass
        #elif slot_type == Node._inverse:     pass

    @timed
    def put_slot_values(kb,frame_or_name,slot, values,
                        slot_type=Node._own,
                        value_selector = Node._known_true,
                        kb_local_only_p = 0):
        (frame,
         frame_found_p) = kb.get_frame_in_kb(frame_or_name,
                                             kb_local_only_p=0)
        if not frame:
            frame = frame_or_name

        frame_name = str(frame)

        if type(values) != type([]): raise CardinalityViolation(values)
        slot_key = str(slot)
        if type(slot) == str:
            slot_obj = kb.get_frame_in_kb(slot)[0]
            if not slot_obj:
                slot_obj = kb.create_slot(slot)
        else:
            slot_obj = slot

        kb_get_behave = kb.get_behavior_values_internal
        if Node._immediate in kb_get_behave(Node._constraint_checking_time):
            current_values = kb.get_slot_values(frame,slot,
                                                inference_level = Node._all,
                                                slot_type = Node._own,
                                                number_of_values = Node._all,
                                                value_selector = Node._either,
                                                kb_local_only_p = 0)
            orig_values = copy.copy(values)
            values = kb.enforce_slot_constraints(frame,slot,
                                                 current_values = current_values,
                                                 future_values = values,
                                                 inference_level = Node._all,
                                                 slot_type = Node._either,
                                                 kb_local_only_p = 0)
            if len(orig_values) <> len(values):
                print "We got shortened."
        #print "put_slot_values(%s,%s,%s,slot_type=%s)" % (frame,slot,values,slot_type)

        del_sql = "delete from kb_frame_slot_values where kb=? and frame=? and slot_type=? and slot=?"
        del_prm = (str(kb),str(frame_name),str(slot_type),str(slot_key))
        cursor = kb._cursor()
        sql_execute(cursor,"begin transaction;")
        sql_execute(cursor,del_sql,del_prm)
        order = 0
        for value in values:
            # All very straight forward but for one piece: we permit
            # different values to be of different types (though almost
            # universally they would be of one type) on the judgement
            # that due to polymorphism it would be possible for
            # different values to have different types.  I suspect
            # though that a slot's range is either a datatype 
            # (ie, int|float|date|str) or is a frame (in which case 
            # the frame name is inserted into the value_str column.
            # The polymorphism should really be contained to the latter
            # case, that is frames, hence value_str would be universally
            # used in that situation.  So: supporting different value_types
            # for the same slot is not ontologically grounded unless a slot
            # can be specifically defined as having a range of EITHER INT or FLOAT
            # for example.  Despite all this I will leave this as it is
            # so we don't have type conversion problems as in some situation where
            # the first value has a non-str type but some subsequent value can not
            # be converted to that non-str type.
            order += 1            
            value_type = get_value_type(value)
            ins_sql = str("insert into kb_frame_slot_values " + \
                              "(kb,frame,slot_type,slot,value_%s,value_type,value_order) " +\
                              "values (?,?,?,?,?,'%s',?)") % (value_type,value_type)
            ins_prm = (str(kb),str(frame_name),str(slot_type),str(slot_key),value,order)
            sql_execute(cursor,ins_sql,ins_prm)

        sql_execute(cursor,"commit;")

        if slot_type == Node._own:
            if slot_obj._the_inverse_of_this_slot <> None:
                inverse_slot = slot_obj._the_inverse_of_this_slot
                # Since we are dealing with a slot with an inverse it can be
                # assumed that the domain and range are both class instances 
                # rather than data types
                for value in values:
                    (inverse_frame,inverse_frame_found_p) = kb.get_frame_in_kb(value,kb_local_only_p=False)
                    if inverse_frame_found_p:
                        (inverse_cardinality,inverse_exact_p) = \
                            kb.get_slot_value(inverse_slot,
                                              Node._SLOT_CARDINALITY)
                        if inverse_exact_p and not inverse_cardinality and \
                                inverse_cardinality == 1:
                            kb.put_slot_value(inverse_frame,inverse_slot,frame,
                                              slot_type=Node._inverse)
                        else:
                            kb.add_slot_value(inverse_frame,inverse_slot,frame,
                                              slot_type=Node._inverse)

    put_slot_values_internal = put_slot_values

    @timed
    def _add_frame_to_store(kb,frame):
        sql = """
        insert into kb_frame_slot_values 
           (kb,frame,slot_type,slot,value_type,value_order,value_str,creation_time) values 
           (?, ?,    ':own',   ?,   'str',     0,          ?        ,datetime('now'))
        """
        try:
            frame_name = str(frame)
        except:
            frame_name = frame._name
        curs = sql_execute(kb._cursor(),
                           sql, 
                           (kb._name,
                            frame_name,
                            'isOfType',
                            str(frame.__class__.__name__)))
        return curs

    def coerce_to_frame_internal(kb,frame):
        if str(kb) == str(frame):
            return kb
        return str(frame)


class SqliteMetaKb(SqliteKb):
    _name = "DefaultMetaKb"

    def coerce_to_frame_internal(kb,frame):
        sql = """select count(*) from kb_frame_slot_values 
                 where kb=? and frame=?"""
        if sql_get_one(kb._cursor(),sql,
                       (str(kb),str(frame))):
            return frame
        return None

    def _get_meta_kb(self):
        return self

    @timed
    def _get_kb_type(kb,thing):
        sql = """select value_str from kb_frame_slot_values 
                 where kb='%s' and frame='%s' and slot='%s' OKNK"""
        args = (str(kb),str(thing),kb._type_slot_name)
        sql = sql % args
        frame_type_name = sql_get_one(kb._cursor(),
                                      sql)
        #print frame_type_name,locals(),globals()
        return locals()[frame_type_name]
        

    @timed
    def get_frame_in_kb_internal(kb,thing,error_p=1,kb_local_only_p=0):
        frame_type = kb._get_kb_type(thing)
        found_frame = frame_type(str(thing))

        if found_frame == None:
            if thing == kb or str(thing) == str(kb):
                found_frame = kb
        # FIXME the whole coercibility issue is ignored
        if found_frame:
            return (found_frame,found_frame != None)
        else:
            return (None,None)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
