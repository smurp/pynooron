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

    def perform_comparison(self,expect=None,got=None,msg=""):
        msg += "\n  expected: %(expect)s\n   but got: %(got)s"
        self.assertEquals(expect,got,msg % locals())


    def GGtest_0010_forward(self):
        mykb = find_kb('InverseMinimal')
        good = """['AliceInWonderland']"""
        resp = list(mykb.get_slot_values('LewisCarroll','Wrote', kb_local_only_p = 0)[0])
        self.assertEquals(good, str(resp))

    def test_0020_inverse(self):
        import pprint
        mykb = find_kb('InverseMinimal')
        good = """['LewisCarroll']"""
        alice = mykb.get_frame_in_kb('AliceInWonderland')[0]
        lewis = mykb.get_frame_in_kb('LewisCarroll')[0]

        resp = list(mykb.get_slot_values('AliceInWonderland','WrittenBy', kb_local_only_p = 0)[0])
        self.assertEquals(1,str(resp).count('LewisCarroll'),"get_slot_values('AliceInWonderland','WrittenBy') <> 'LewisCarroll'")
                
        self.perform_comparison(
            msg    = "",
            expect = set([lewis]),
            #expect = set(mykb.get_frame_in_kb('WrittenBy')[0]),
            got    = set(alice._inverse_slots.get('WrittenBy')))
            
        self.perform_comparison(
            msg = "_inverse_slots do not merge right?",
            expect = set([mykb.get_frame_in_kb('JohnVonNeumann')[0],
                          mykb.get_frame_in_kb('OskarMorgenstern')[0]]),
            got = set(mykb.get_slot_values('TheoryOfGamesandEconomicBehaviour','WrittenBy')[0]))
                          


if __name__ == "__main__":
    unittest.main()
