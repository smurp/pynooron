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
    print_frame('SamuelBeckett')
    print get_class_superclasses('AdultHuman')
    print_frame('Human')
    print_frame('Age')
    print_frame('Species')
    print get_slot_values('Species',':DOCUMENTATION-IN-FRAME')
