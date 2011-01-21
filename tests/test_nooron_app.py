#!/usr/bin/env python

__version__='$Revision: 1.18 $'[11:-2]
__cvs_id__ ='$Id: test_pyokbc.py,v 1.18 2003/05/22 20:28:39 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('..')
from pyokbc import *
PyOkbc.DEBUG=0
def str_sort(a,b):
    return cmp(str(a),str(b))


def copy_same_as_original(self,src_kb,loc):
    mykb = open_kb(src_kb)
    #goto_kb(mykb)
    print "======================",src_kb,mykb.__class__    
    src_fname = mykb._file_name()
    prefix = '~/tmp/DELETEME_Copy_of_'
    mykb.save_kb_as(prefix+src_kb)
    a = open(loc+src_fname)
    #b = open(loc+'DELETEME_'+src_fname)
    b = open(prefix+src_kb)
    a_all = string.join(a.readlines(),"\n")
    b_all = string.join(b.readlines(),"\n")
    a.close()
    b.close()
    self.assertEquals(a_all,b_all)

from test_enhancements import *
class ReadOnlyTestCase(unittest.TestCase,TestEnhancements):
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
                  cwd+'/../know']
        
        os.environ["LOCAL_CONNECTION_PLACE"] = string.join(places,':')
        #std_tranny = open_kb("standard_transmission_fsa")
        mykb = open_kb("smurp_web_log")
        goto_kb(mykb)

    def test_get_class_instances_of_web_log_entry(self):
        contains = set_of_strings(
            "wle_0001 wle_0002 wle_0003 wle_0004 wle_0005 wle_0006 wle_0007".split())
        self.perform_comparison(
            msg      = "some web log entries missing",
            contains = contains,
            got      = set_of_strings(get_class_instances('web_log_entry')[0]))

    def test_get_class_instances_of_web_log_entry(self):
        goto_kb(meta_kb())
        self.perform_comparison(
            msg      = "some web log entries missing",
            contains = set([]),
            got      = set_of_strings(get_class_instances('nooron_app_class')[0]))

    
class Bogus:
    pass

if __name__ == "__main__":
    unittest.main()
    
