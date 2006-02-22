#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_ZfsKb.py,v 1.1 2006/02/21 17:49:03 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *
from pyokbc.FileSystemKb import ZfsKb

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

class ZfsKbStuff(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()

        spec_loc = create_kb_locator('Species.zfskb')
        mykb = create_kb("Species",kb_type=ZfsKb,kb_locator=spec_loc)
        goto_kb(mykb)

    def test_make_a_frame(self):
        create_class('LifeOnEarth')
        kingdom = create_class('BiologicalKingdom')
        monera = create_class('Monera',direct_types=[kingdom])
        animalia = create_class('Animalia',direct_types=[kingdom])
        # To get into the debugger:
        #  http://www.gossamer-threads.com/lists/zope/users/184928
        # once in the debugger:
        #  (Pdb) u
        #  (Pdb) p state['_container']['Animalia']._kb.__dict__
        save_kb()
        
        
if __name__ == "__main__":
    unittest.main()

