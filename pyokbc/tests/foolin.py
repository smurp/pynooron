#!/usr/bin/python2.1

"""
TODO moved to pyokbc/TODO

"""

import sys
sys.path.append('../..')
from pyokbc import *
import os

os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()

#goto_kb(Node._primordial_kb)
#dump_kb(current_kb())

if 0:
    for i in Node._constraints_checked_all:
        print i
    if Node._VALUE_TYPE in Node._constraints_checked_all:
        print "found it!"
    else:
        print "Not found"

if 1:
    mykb = open_kb("PeopleData.pykb")
    goto_kb(mykb)

if 0:
    print_frame('SamuelBeckett')
    print get_class_superclasses('AdultHuman')
    print_frame('Human')
    print_frame('Age')
    print_frame('Species')
    print get_slot_values('Species',':DOCUMENTATION')
    print "SamuelBeckett Eats",get_slot_values('SamuelBeckett','Eats',
                                               slot_type=Node._all)[0]
    print "instance types of Beckett:",get_instance_types('SamuelBeckett')

if 1:
    #beck = get_frame_in_kb('SamuelBeckett')[0]
    #print beck._own_slots
    alice = get_frame_in_kb('AliceLidell')[0]
    #print alice._own_slots
    print get_slot_value('AliceLidell',Node._DOCUMENTATION,
                         slot_type=Node._all)[0]
