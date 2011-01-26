#!/usr/bin/env python

__version__='$Revision: 1.18 $'[11:-2]
__cvs_id__ ='$Id: test_pyokbc.py,v 1.18 2003/05/22 20:28:39 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('..')
sys.path.append('../..')
from pyokbc import *
PyOkbc.DEBUG=0
def str_sort(a,b):
    return cmp(str(a),str(b))

def copy_same_as_original(self,src_kb,loc):
    mykb = open_kb(src_kb)
    #goto_kb(mykb)
    print "======================",src_kb,mykb.__class__    
    src_fname = mykb._file_name()
    prefix = 'DELETEME_Copy_of_'
    mykb.save_kb_as(prefix+src_kb)
    a = open(loc+src_fname)
    #b = open(loc+'DELETEME_'+src_fname)
    b = open(prefix+src_kb)
    a_all = string.join(a.readlines(),"\n")
    b_all = string.join(b.readlines(),"\n")
    a.close()
    b.close()
    self.assertEquals(a_all,b_all)


class ReadOnlyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)

        home_dir  = os.path.expanduser("~")
        cache_path = '%(home_dir)s/tmp/nooron_cache' % locals()
        cwd = os.getcwd()
        kr_root = '%(home_dir)s/knowledge/' % locals()
        places = [kr_root+'apps_of/nooron',
                  kr_root+'apps_of/smurp',          
                  kr_root+'apps_of/givingspace',
                  kr_root+'apps_of/demo',
                  kr_root+'apps_of/kaliya',
                  kr_root+'nooron_apps',
                  kr_root+'nooron_foundations',
                  cwd+'/../../know']
        
        os.environ["LOCAL_CONNECTION_PLACE"] = string.join(places,':')
        #std_tranny = open_kb("standard_transmission_fsa")
        mykb = open_kb(meta_kb())
        goto_kb(mykb)


    def perform_comparison(self,expect=None,got=None,msg=""):
        msg += "\n  expected: %(expect)s\n   but got: %(got)s"
        if type(expect) == set and type(got) == set:
            missing = expect.difference(got)
            extra   = got.difference(expect)
            if missing:
                msg += "\n   missing: %(missing)s"
            if extra:
                msg += "\n    extra: %(extra)s"
        self.assertEquals(expect,got,msg % locals())

    def test_0001_what_is_breaking_auto_create_links(self):
        goto_kb(meta_kb())
        ckb = current_kb()
        self.assertEquals(meta_kb(),ckb,"%s should really be %s" % (ckb,meta_kb()))
        self.assertNotEquals(type(ckb),str,
                             'the meta_kb should not be of type %s for gods sake' % type(ckb))
        self.assertEquals(str(ckb),'doh')
        count = 0
        nooron_app_classes = get_class_instances('nooron_app_class')[0]
        self.assertNotEquals(nooron_app_classes,[],'nooron_app_classes should not be []')
        for inst in nooron_app_classes:
            count += 1
            self.assertNotEquals(type(inst),str,"'%s' should not be a %s" % (inst,type(inst)))
        self.assertNotEquals(0,0,"oh, there were no instances of 'nooron_app_class'")
        for inst in get_class_instances('nooron_app_class')[0]:
            count += 1
            self.assertNotEquals(type(inst),str,"'%s' should not be a %s" % (inst,type(inst)))
        self.assertNotEquals(0,0,"oh, there were no instances of 'nooron_app_class'")



if __name__ == "__main__":
    unittest.main()
    
