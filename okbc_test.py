#!/usr/bin/python

from OKBC import *
from OkbcPythonKb import OkbcPythonKb

mykb = OkbcPythonKb()
#mykb = TupleKb()
goto_kb(mykb)

FoodsSlot = SLOT('Foods',mykb)
Age = SLOT('Age',mykb)

Thing  = create_class('Thing')

Food   = create_class('Food',direct_superclasses = [Thing])
Berry = create_class('Agent',direct_superclasses = [Food])
Cookie = create_class('Agent',direct_superclasses = [Food])
Apple = create_class('Agent',direct_superclasses = [Food])

Agent  = create_class('Agent',direct_superclasses = [Thing])
Person = create_class('Person',direct_superclasses = [Agent])
Child  = create_class('Child',direct_superclasses = [Person])

Ethan = create_individual('Ethan',
                          direct_types=[Child],
                          own_slots = ((Age,3),
                                       (FoodsSlot,
                                        (Node._default,Berry),
                                        Cookie)),
                          pretty_name = 'Ethan Brown')

Sam = create_individual('Sam',
                        kb=mykb,
                        direct_types=[Child],
                        own_slots = ((Age,3),
                                     (FoodsSlot,
                                      Apple,
                                      Berry,
                                      Cookie)),
                        pretty_name = 'Ethan Brown')



#for frame in get_kb_frames():
#    dump_frame(frame)
#    print " "

mykb.save_kb()
