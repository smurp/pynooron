#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_PyKb.py,v 1.1 2003/02/13 11:56:49 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *

def str_sort(a,b):
    return cmp(str(a),str(b))

# test for
##  only save frames which are local to the kb   

class ReadOnlyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        addenda = open_kb("Addenda")
        mykb = open_kb("OtherPeople")
        mykb = open_kb("PeopleData")
        goto_kb(mykb)


    def test_save_as(self):
        save_kb_as('someplace.py')
        #self.assertEquals(good, str(resp))
        

if __name__ == "__main__":
    unittest.main()
