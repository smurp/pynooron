
from AbstractSqlKbTypes import *

import sqlite


class AbstractSqliteKb:
    """The Abstract Kb that is meant to contain the majority of Sqlite-isms.

    The intension is that this class will be combined with AbstractSqlKbTypes
    like:  Sqlite_Assertion_Kb_Type(AbstractSqliteKb,Assertion_Sql_Kb_Type)
    """
    def _table_exists_p(self,table_name):
        sql = '.table %s' % table_name
        curs = self._sql_conn.cursor()
        curs.execute(sql)
        return len(curs.fetchall()) == 1
        
class Sqlite_Assertion_Kb_Type(AbstractFileKb,CachingMixin,
                               SqliteKb,Assertion_Sql_Kb_Type):
    _kb_type_file_extension = 'sqlitekb'
    make_backups = 0
    via_temp = 0

    def __init__(self,kb_locator,connection,name=None,initargs={}):
        if type(filename_or_kb_locator) == type({}):
            self._locator = filename_or_kb_locator
            self._name = self._locator['kb_name']
            self._file_uri = self._locator['file_uri']
            self._filename = self._file_uri
            filename = self._file_uri # should convert from uri
            name = self._name
        else:
            raise "expecting filename_or_kb_locator as dict"
        
        self._place = place
        self._connection = connection
        self._opened = False
        AbstractFileKb.__init__(self,name,connection=connection)
        CachingMixin.__init__(self)

        
    def open_kb_internal(self,kb_type = None,erro_p = True):
        if self._opened:
            return self
        connection = self._connection
        name = self._name
        self._sql_connect(self._filename)
        self._ensure_triple_table_exists()

        
        
    def create_kb(self,name,kb_locator=None,initargs={},connection=None):   pass
    
