#!/usr/bin/env python2.1

__version__='$Revision: 1.4 $'[11:-2]
__cvs_id__ ='$Id: test_primordial.py,v 1.4 2002/11/26 20:32:12 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *

def str_sort(a,b):
    return cmp(str(a),str(b))


class PrimordialTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        mykb = open_kb("PeopleData")
        goto_kb(mykb)

    def test_all_classes_instances_of_CLASS(self):
        # see CLASS_RECURSION in PyOkbc.py
        for klass in get_kb_classes():
            if not (klass in []):
                self.failUnless(instance_of_p(klass,Node._CLASS)
                                ,"%s not instance of %s" % (klass,Node._CLASS))

    def test_all_classes_subs_of_THING(self):
        # see CLASS_RECURSION in PyOkbc.py
        for klass in get_kb_classes():
            if not (klass in [Node._THING]):
                self.failUnless(subclass_of_p(klass,Node._THING)
                                ,"%s not sub of %s" % (klass,Node._THING))

    def test_get_class_superclasses_of_THING(self):
        good = "[]"
        resp = list(get_class_superclasses(':THING')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))


    def test_get_frame_slots_of_THING(self):
        good = "[':DOCUMENTATION']"
        resp = list(get_frame_slots(':THING')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))

    def test_get_slot_value_of_THING_DOCUMENTATION(self):
        good = "[':DOCUMENTATION']"
        resp = get_slot_value(':THING',':DOCUMENTATION')[0]
        self.assertNotEquals(-1,resp.find('http'))

    def test_get_kb_direct_children_PRIMORDIAL_KB(self):
        good = "[]"
        primal = find_kb('PRIMORDIAL_KB')
        resp = get_kb_direct_children(kb=primal)
        self.assertEquals(good,str(resp))

    def test_get_kb_direct_parents_PRIMORDIAL_KB(self):
        good = "[]"
        primal = find_kb('PRIMORDIAL_KB')
        resp = get_kb_direct_parents(kb=primal)
        self.assertEquals(good,str(resp))

if __name__ == "__main__":
    unittest.main()
