#!/usr/bin/python2.1

"""
TODO

The _primordial_kb elements are all defined after we have already
used the original Symbol values. Doh? There are a bunch of equality tests
which this should break.

* PyOkbc must support operations minimally required by Nooron:
** multiple parallel KBs (ie meta_kb)
** default values  [so there can be default values for assocated NPTs]
** value inheritance, from class to individual (template_slots)
*** coerce_to_handle [how the hell does a handle work]

* move get_class_superclasses to KB or TupleKb

"""

import sys
sys.path.append('..')
from pyokbc import *

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
    mykb = open_kb("smurp_web_log.pykb")
    goto_kb(mykb)
    
    #dump_kb(mykb)
    #for klass in get_kb_classes():
    #    dump_frame(klass)
    #for klass in get_class_subclasses('nooron_schema_class')[0]:
    print get_class_superclasses('gear')
    for klass in get_class_subclasses('web_log_category')[0]:
        dump_frame(klass)
