#!/usr/bin/env python2.1

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *


class ClassHierarchyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        mykb = open_kb("PeopleData.pykb")
        goto_kb(mykb)
        
    def test_get_class_superclasses(self):
        resp = get_class_superclasses('AdultHuman')
        lst = list(resp[0])
        lst = map(str,lst)
        lst.sort()
        supers = [lst,resp[1],resp[2]]
        superstring = str(supers)
        good = "[['Agent', 'Animal', 'Human', 'Mammal', 'Primate', 'Thing'], 1, 0]"
        self.assertEquals(superstring,good)

    def test_get_frame_sentences(self):
        good = \
             """(individual SamuelBeckett)\n""" + \
             """(instance-of SamuelBeckett AdultHuman)\n""" + \
             """(slot Age SamuelBeckett 83)\n""" + \
             """(slot BirthTime SamuelBeckett "1906-04-13 GMT")\n""" + \
             """(slot Eats SamuelBeckett "Apple")\n""" + \
             """(slot Eats SamuelBeckett "Berry")\n""" + \
             """(slot Eats SamuelBeckett "Cookie")"""
        resp = list(get_frame_sentences('SamuelBeckett')[0])
        resp.sort()
        self.assertEquals(good, string.join(resp,"\n"))

if __name__ == "__main__":
    unittest.main()
