#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_BrainKb.py,v 1.1 2003/05/13 16:28:14 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *

def str_sort(a,b):
    return cmp(str(a),str(b))

def copy_same_as_original(self,src_kb,loc):
    mykb = open_kb(src_kb)
    #goto_kb(mykb)
    #print "======================",src_kb,mykb.__class__    
    src_fname = mykb._file_name()
    mykb.save_kb_as('DELETEME_Copy_of_'+src_kb)
    a = open(loc+src_fname)
    #b = open(loc+'DELETEME_'+src_fname)
    #b = open('DELETEME_'+src_fname)
    b = open('DELETEME_Copy_of_'+src_kb)    
    a_all = string.join(a.readlines(),"\n")
    b_all = string.join(b.readlines(),"\n")
    a.close()
    b.close()
    self.assertEquals(a_all,b_all)

class BrainKbStuff(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()

        mykb = open_kb("WorldEncyclopedia")
        mykb = open_kb("InternetPortsAndProtocols")
        mykb = open_kb("elements")        
        mykb = open_kb("FamousQuotations")        
        #print "class is",mykb.__class__
        goto_kb(mykb)

    def test_get_kb_classes(self):
        we = find_kb('WorldEncyclopedia')
        self.assertEquals(str(get_kb_classes(kb=we,
                                             kb_local_only_p=1)[0]),
                          'Country')

    def test_UnitedStates(self):
        good = 'United States dollars'
        we = find_kb('WorldEncyclopedia')
        self.assertEquals( get_slot_value('UnitedStates','Currency',
                                          kb=we)[0],good)
        
        
if __name__ == "__main__":
    unittest.main()

