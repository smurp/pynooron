#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_okbcop.py,v 1.1 2003/06/19 21:47:21 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('..')
sys.path.append('../code')
from pyokbc import *
PyOkbc.DEBUG=0
def str_sort(a,b):
    return cmp(str(a),str(b))

import OkbcOperation

class OkbcOperationsTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)

        #cwd = os.getcwd()
        #kr_root = '/home/smurp/knowledge/'
        #places = [kr_root+'apps_of/nooron',
        #          kr_root+'apps_of/smurp',          
        #          kr_root+'apps_of/givingspace',
        #          kr_root+'apps_of/demo',
        #          kr_root+'apps_of/kaliya',
        #          kr_root+'nooron_apps',
        #          kr_root+'nooron_foundations',
        #          cwd+'/../know']
        
        #os.environ["LOCAL_CONNECTION_PLACE"] = string.join(places,':')
        #std_tranny = open_kb("standard_transmission_fsa")
        #mykb = open_kb("smurp_web_log")
        #goto_kb(mykb)

    def test_make_wiki_word(self):
        for good,input in [('WikiWord','wiki word'),
                           ('1','1'),
                           ('1WackyWikiWord','1 wacky  wiki word'),
                           ('','   '),
                           ('12','1 2')]:
            self.assertEquals(good,
                              OkbcOperation.make_wiki_word(input))

        
    def test_name_automatically(self):
        nameit = OkbcOperation.make_good_name
        for good,form in [('WekeyWord',{'name':'',
                                       'pretty_name':['wekey word']}),
                          ('MorfWoof',{'name':'MorfWoof',
                                       'pretty_name':['']}),
                          ('somenumber',{'name':None,
                                       'pretty_name':['']}),
                          
                           ]:
            newname = nameit(form,'','name')
            if string.find(newname,'ZQ') == -1:
                self.assertEquals(newname,good)

        


if __name__ == "__main__":
    unittest.main()
    
