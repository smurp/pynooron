#!/usr/bin/env python2.1

__version__='$Revision: 1.3 $'[11:-2]
__cvs_id__ ='$Id: test_PyKb.py,v 1.3 2003/02/14 19:47:30 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *

def str_sort(a,b):
    return cmp(str(a),str(b))

class PyKbStuff(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        mykb = open_kb("PeopleData")
        goto_kb(mykb)

    def test_save_is_same_as_original(self):
        test_kb_name = 'DELETEME_Copy_of_PeopleData'
        save_kb_as(test_kb_name)
        a = open('PeopleData.pykb')
        b = open(test_kb_name)
        a_all = string.join(a.readlines(),"\n")
        b_all = string.join(b.readlines(),"\n")
        a.close()
        b.close()
        self.assertEquals(a_all,b_all)

    def test_save_kb(self):
        save_kb()
        
if __name__ == "__main__":
    unittest.main()
