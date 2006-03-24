
"""
These 

How to do this against multiple relational backends?!?
I will proceed by doing psql and sqlite simultaneously.



"""

def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')

class Abstract_Sql_Kb_Type:
    def _sql_connect(self,*args,**kwargs):
        abstract()

class Assertion_Sql_Kb_Type(Abstract_Sql_Kb_Type): 
    """Persist knowledge via an SQL schema of assertion form.
    
    Conceptually, the schema is:
  CREATE TABLE sentences(
    subject varchar,
    verb    varchar,
    object  varchar)

Then records are:
  Subject|Verb|Object
  =======|====|===========
  Charles|HasBiologicalParent|Elizabeth
  Charles|HasBiologicalParent|Philip
  Elizabeth|IsInstanceOf|Queen
  Queen|IsSubclassOf|Woman
  Queen|IsSubclassOf|Monarch
  Monarch|IsSubclassOf|Royalty
  Woman|IsSubclassOf|Human
  HasMother|IsInstanceOf|:SLOT
  Charles|HasLifeEvents|CharlesWasBorn
  Charles|HasLifeEvents|CharlesMarriedDiana
  Charles|HasLifeEvents|DianaDivorcedCharles
  HasLifeEvents|IsInstanceOf|:SLOT
  HasLifeEvents|:SLOT-VALUE-TYPE|:SEQUENCE   -- imposes order on values
  
  Notice that it would be derivable that Charles was a Human?  Though
  we could cache that explicitly about that for speed.

This slightly fancier structure would perform better with SQL indexing:
  CREATE TABLE sentence(
    subject varchar,
    verb varchar,
    object_id int, -- sequence to impose optional order eg HasLifeEvents
    object_int int,
    object_int varchar,
    object_real real,
    type_of_object varchar in ('int','varchar','real'),
    primary key (subject,verb,object_id)
  )

Pros:
  Complete fluidity of ontological change because it is pure knowledge.
Cons:
  Performance is a bit poorer than conventional schemae, though
    retrieving all the fields for Charles, for instance, is just a
    single query.  Understanding what they mean is more queries!
    Such things are cachable, of course.  Indeed the ontology would
    usually live in a separate text file.
  Other software accessing the SQL db would have to adapt to the
    sentence/assertion style of doing things.
KnownUses:
  Chris and Shawn did this in java and perl against SolidSQL.
  A similar structure was used in LABBASE for AHLB!
    """
    
    _table_name = 'triple'
    _create_table_sql = """
    create table triple (
      subject       varchar,
      verb          varchar,
      object_id     int,
      object_int    int,
      object_real   real,
      object_str    varchar,
      primary key   (subject,verb,object_id)
    )
    """
    def _ensure_triple_table_exists(self):
        if not self._table_exists_p(self._table_name):
            self._create_table(self._create_table_sql)
                               
            

class Sql_Schema_From_Onto_Kb_Type(Abstract_Sql_Kb_Type):
    """
We maintain the Ontology in a text file format (as RDF, TopicMap, KIF,
or .pykb) and then have an SQL backend which has tables where the
ontology has classes, records for knowledge instances, columns for
slots, etc.  When the ontology changes (and we ask for the change to be
pushed to the schema) then ALTER TABLE operations would happen.

Pros:
  Easy for other software to access the data in the SQL tables.
  Probably pretty good performance
Cons:
  Harder to write the backend.
  More differences between backends for psql vs. mysql vs. sqlite
  Some complexities during ontological evolution because schema
    evolution is not the same thing.
"""
    pass


class Onto_From_Sql_Schema_Kb_Type(Abstract_Sql_Kb_Type):
    """
Automatically introspect an SQL schema and deduce an ontology on the fly
(which is cached) then manually layer more ontology on top to fine-tune
things.

Pros:
  Adapt to legacy databases.
  Developers work in familiar SQL to ontologize.
Cons:
  Not all legacy databases are well suited to such introspection because
    of denormalization or other weirdnesses.
  Relatively difficult to write such a backend.
  """
    pass

class Custom_Sql_Kb_Type(Abstract_Sql_Kb_Type):
    """
4) CustomizeABackendForASchema
==============================
Probably a good approach for PyRETS relational schema, because it
doesn't have to change often and then we can get quite good knowledge
impedance matching in the result.

Pros:
  Solves impedance matching problem.
  Essentially perfect inter-operation is achievable.
  Could leverage some toolkit code for doing such things.
Cons:
  There would be an python programming investment in each relational
    schema.
  Not an automatic process.
  When schema changes, there might be some programming to do.
  """
    pass

