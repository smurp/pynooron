#!/usr/bin/python

from OKBC import *

#print Node._all
#print Node._slot_types

mykb = MemoryKb()

sam = INDIVIDUAL('sam',mykb)
FoodsSlot = SLOT('Foods',mykb)
Berry = KLASS('Berry',mykb)
Cookie = KLASS('Cookie',mykb)
Apple = KLASS('Apple',mykb)
Age = SLOT('Age',mykb)

Child = KLASS('Child',mykb)

ethan = create_individual('Ethan',kb=mykb,
                          direct_types=[Child],
                          own_slots = ((Age,3),
                                       (FoodsSlot,
                                        (Node._default,Berry),
                                        Cookie)),
                          pretty_name = 'Ethan Brown')

sam.put_slot_values(FoodsSlot,[])
sam.put_slot_value(FoodsSlot,Cookie)
sam.put_slot_values(FoodsSlot,[Apple,Berry,Cookie])

sam.put_slot_values(Age,[1])

for slot in sam.get_frame_slots():
#    slot = str(slot)
    print "Slot:", slot
    print "   values: "+str(sam.get_slot_values(slot)[0])
    

