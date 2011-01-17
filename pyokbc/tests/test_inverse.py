#!/usr/bin/env python

__version__='$Revision: 1.25 $'[11:-2]
__cvs_id__ ='$Id: test_funcs.py,v 1.25 2006/03/21 20:48:06 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *
from debug_tools import timed

def str_sort(a,b):
    return cmp(str(a),str(b))

class ReadOnlyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()

    def test_0010_forward(self):
        mykb = find_kb('InverseMinimal')
        good = """['AliceInWonderland']"""
        resp = list(mykb.get_slot_values('LewisCarroll','Wrote',
                                         kb_local_only_p = 0)[0])
        #resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0020_inverse(self):
        mykb = open_kb('InverseMinimal')
        good = """['LewisCarroll']"""
        resp = list(mykb.get_slot_values('AliceInWonderland','WrittenBy',
                                         kb_local_only_p = 0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

if __name__ == "__main__":
    unittest.main()
