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
** merging KBs (parent_kbs) for the NooronApp architecture
** refering to frames by frame_name
*** coerce_to_frame
*** coerce_to_handle

"""

from PyOkbc import *

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
    mykb = open_kb("t/PeopleData.pyokbc")
    goto_kb(mykb)
    for f in get_kb_frames(kb_local_only_p=1):
        print f
    #save_kb_as('/tmp/booger.pyokbc')
    #dump_kb(mykb)
    #(AdultHuman,w) = get_frame_in_kb('AdultHuman')
    #print "====\n", AdultHuman
    #print_frame(AdultHuman)
    #dump_frame(AdultHuman)
    #dump_frame('Sam')
    #print_frame('Sam')
    #print get_class_superclasses(AdultHuman)
    #print get_class_superclasses('Human')
