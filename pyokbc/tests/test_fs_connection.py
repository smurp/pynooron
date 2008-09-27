#!/usr/bin/env python

__version__='$Revision: 1.6 $'[11:-2]
__cvs_id__ ='$Id: test_fs_connection.py,v 1.6 2008/09/26 20:45:33 smurp Exp $'

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
        cwd =  os.getcwd()
        places =  [cwd,cwd+'/more']
        place_path = string.join(places,':')
        os.environ["LOCAL_CONNECTION_PLACE"] = place_path
        goto_kb(meta_kb())

    def test_open_kb_without_extension(self):
        good = 'MergeKB'
        merge_kb = open_kb('MergeKB')
        self.assertEquals(good,str(merge_kb))

    def test_open_kb_along_path(self):
        good = 'Silly'
        merge_kb = open_kb('SillyChild')
        self.assertEquals(good,str(merge_kb))

    def skip_test_openable_kbs(self):
        good = 'MergeKB'
        resp = openable_kbs()
        self.assertEquals(good,str(resp))

    def skip_test_retrieve_file_from_meta_kb(self):
        good = 'test_fs_connection.py'
        resp = get_frame_in_kb('test_fs_connection.py')[0]
        self.assertEquals(good,str(resp))


if __name__ == "__main__":
    unittest.main()
