#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_fs_connection.py,v 1.1 2002/11/26 20:32:12 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *

def str_sort(a,b):
    return cmp(str(a),str(b))

class FSConnectionTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        goto_kb(meta_kb())

    def test_open_kb_without_extension(self):
        good = 'MergeKB.pykb'
        merge_kb = open_kb('MergeKB')
        self.assertEquals(good,str(merge_kb))

    def test_retrieve_file_from_meta_kb(self):
        good = 'test_fs_connection.py'
        resp = get_frame_in_kb('test_fs_connection.py')[0]
        self.assertEquals(good,str(resp))


if __name__ == "__main__":
    unittest.main()
