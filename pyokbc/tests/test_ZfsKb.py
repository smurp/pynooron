#!/usr/bin/env python2.1

__version__='$Revision: 1.4 $'[11:-2]
__cvs_id__ ='$Id: test_ZfsKb.py,v 1.4 2006/03/19 16:55:16 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *
from pyokbc.FileSystemKb import ZfsKb

NUM_BACTERIA = 100

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


    def new_kb(self):
        #os.system("rm -f Species.zfskb*")
        spec_loc = create_kb_locator('Species',kb_type = ZfsKb)
        #print "spec_loc =",spec_loc
        #meta_kb().print_frame(spec_loc)
        mykb = create_kb("Species",kb_locator=spec_loc)
        #mykb = create_kb(spec_loc)
        goto_kb(mykb)


    def test_0020_make_a_frame(self):
        self.new_kb()
        create_class('LifeOnEarth')
        kingdom = create_class('BiologicalKingdom',
                               pretty_name="Biological Kingdom")
        create_class('Monera',
                     own_slots=[[':DOCUMENTATION-LINK',
                                 'http://en.wikipedia.org/wiki/Monera']],
                     direct_superclasses=[kingdom])
        create_class('Animalia',
                     own_slots=[[':DOCUMENTATION-LINK',
                                 'http://en.wikipedia.org/wiki/Animalia']],
                     direct_superclasses=[kingdom])
        create_class('Protista',
                     own_slots=[[':DOCUMENTATION-LINK',
                                 'http://en.wikipedia.org/wiki/Protista']],
                     direct_superclasses=['BiologicalKingdom'])
        create_class('Plantae',
                     own_slots=[[':DOCUMENTATION-LINK',
                                 'http://en.wikipedia.org/wiki/Plantae']],
                     direct_superclasses=['BiologicalKingdom'])
        create_class('Fungi',
                     own_slots=[[':DOCUMENTATION-LINK',
                                 'http://en.wikipedia.org/wiki/Fungi']],
                     direct_superclasses=['BiologicalKingdom'])
                     
        # To get into the debugger:
        #  http://www.gossamer-threads.com/lists/zope/users/184928
        # once in the debugger:
        #  (Pdb) u
        #  (Pdb) p state['_container']['Animalia']._kb.__dict__
        save_kb()
        #close_kb()
        

    def test_0030_get_class_superclasses(self):
        #self.new_kb()
        meta = meta_kb()
        print meta._v_store.keys()
        spec_loc = find_kb_locator('Species',
                                   #kb_type = ZfsKb
                                   )
        my_kb = open_kb(spec_loc)
        goto_kb(my_kb)
        #print get_frame_details('Animalia',inference_level='DIRECT')
        resp = list(get_class_superclasses('Animalia')[0])
        resp.sort(str_sort)
        good = "[:THING, BiologicalKingdom]"
        self.assertEquals(good,str(resp))
        close_kb()

class Bogus:

    def test_0040_get_class_subclasses(self):
        """get_subclasses"""

        my_kb = open_kb('Species')
        goto_kb(my_kb)
        #print get_frame_details('Animalia',inference_level='DIRECT')
        resp = list(get_class_subclasses('BiologicalKingdom')[0])
        resp.sort(str_sort)
        good = "[Animalia, Fungi, Monera, Plantae, Protista]"
        self.assertEquals(good,str(resp))

    def test_0050_make_many_bacteria(self):
        """Make Many Bacteria"""
        species = open_kb('Species') 
        goto_kb(species)

        monera = get_frame_in_kb('Monera')[0]
        for i in range(0,NUM_BACTERIA):
            species.create_individual('Species_'+str(i),
                                      direct_types=[monera])
        close_kb(save_p=1)

    def test_0060_retrieve_many_bacteria(self):
        """Retrieve Many Bacteria """
        species = open_kb('Species') 
        goto_kb(species)
        inst = get_class_instances('Monera')
        len_inst = len(inst[0])
        #print len_inst," of Monera"
        #if len_inst < 10:
        #    print inst
        self.assertEquals(len_inst,NUM_BACTERIA)
        close_kb()
            
            
    
if __name__ == "__main__":
    unittest.main()

