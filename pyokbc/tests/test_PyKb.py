#!/usr/bin/env python

__version__='$Revision: 1.7 $'[11:-2]
__cvs_id__ ='$Id: test_PyKb.py,v 1.7 2003/04/13 23:18:55 smurp Exp $'

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

class PyKbStuff(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        mykb = open_kb("PeopleData")
        #print "class is",mykb.__class__
        goto_kb(mykb)

    def skip_test_copy_same(self):
        src_kb = "PeopleData"
        loc = ''
        copy_same_as_original(self,src_kb,loc)

    def skip_test_save_is_same_as_original(self):
        nom = 'OtherPeople'
        prev_kb = current_kb()
        nom_kb = open_kb(nom)
        goto_kb(nom_kb)
        test_kb_name = 'DELETEME_' + nom
        nom_kb.save_kb()
        goto_kb(prev_kb)
        a = open(nom + '.pykb')
        b = open(test_kb_name + '.pykb')
        a_all = string.join(a.readlines(),"\n")
        b_all = string.join(b.readlines(),"\n")
        a.close()
        b.close()
        self.assertEquals(a_all,b_all)

    def test_save_kb_as(self):
        nom = 'OtherPeople'
        prev_kb = current_kb()
        nom_kb = open_kb(nom)
        goto_kb(nom_kb)
        test_kb_name = 'DELETEME_Copy_of_' + nom
        nom_kb.save_kb_as(test_kb_name)
        goto_kb(prev_kb)
        a = open(nom + '.pykb')
        b = open(test_kb_name + '.pykb')
        a_all = string.join(a.readlines(),"\n")
        b_all = string.join(b.readlines(),"\n")
        a.close()
        b.close()
        self.assertEquals(a_all,b_all)
        new_kb = find_kb(test_kb_name)
        print "found new kb",new_kb
        print "found old kb",find_kb(nom)


    def test_ModificationTime(self):
        current = current_kb()
        goto_kb('MergeKB')
        MTIME = get_slot_value(current_kb(),'MTIME')
        ModTime = get_slot_value(current_kb(),'ModificationTime')
        self.assertEquals(MTIME,ModTime)

        pair = []
        def pushpair(self,pair):
            new = get_slot_value(current_kb(),'ModificationTime')[0]
            #print "XX new",[new]
            pair.append(new)
            if len(pair) > 2:
                pair.pop(0)
            if len(pair) == 2:
                #print 'XX pair',pair
                self.assertNotEquals(pair[0],pair[1])
                
        pushpair(self,pair)
        put_slot_value('SamuelBeckett','Age',87)
        pushpair(self,pair)
        create_class('BigWheel')
        pushpair(self,pair)
        add_class_superclass('BigWheel','Person')
        pushpair(self,pair)
        create_individual('TheDude',direct_types=['Person'])
        pushpair(self,pair)
        create_slot('HairColor',own_slots=[[':DOMAIN','Person']])
        pushpair(self,pair)
        create_facet('Validity')
        pushpair(self,pair)

        goto_kb(current)

    def test_ModificationTime(self):
        MTIME = get_slot_value(current_kb(),'MTIME')
        ModTime = get_slot_value(current_kb(),'ModificationTime')
        self.assertEquals(MTIME,ModTime)
        
        
if __name__ == "__main__":
    unittest.main()


"""
(defmethods save-kb-as-internal
    ((new-name-or-locator t)
     (kb (file-mixin file-structure-kb file-tell&ask-defaults-structure-kb)))
  (let ((loc (create-kb-locator-internal
              new-name-or-locator kb (connection kb))))
    (setf (name kb) (name loc))
    (put-frame-name-internal kb (name kb)
                             (meta-kb-internal (connection kb)) t)
    (put-slot-value-internal kb :locator loc
                             (meta-kb-internal (connection kb))
                             :own :known-true t)
    (save-kb-internal kb t)))



"""
