#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_pyokbc.py,v 1.1 2002/11/08 21:22:00 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('..')
from pyokbc import *
PyOkbc.DEBUG=0
def str_sort(a,b):
    return cmp(str(a),str(b))

class ReadOnlyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd() + '/../know'
        mykb = open_kb("smurp_web_log.pykb")
        goto_kb(mykb)

    def test_get_class_instances_of_marvel(self):
        good = "[wle_1, wle_2]"
        resp = list(get_class_instances('marvel')[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_frame_slots_all_gear(self):
        good = "[':DOCUMENTATION', 'npt_for_self']"
        resp = list(get_frame_slots('web_log_category',
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_frame_slots_all_web_log_category(self):
        good = "[':DOCUMENTATION', 'npt_for_self']"
        resp = list(get_frame_slots('web_log_category',
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_frame_slots_all_THING(self):
        good = "['npt_for_self']"
        resp = list(get_frame_slots(':THING',
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_gear(self):
        good = "[:CLASS, :THING, web_log_category]"
        resp = list(get_instance_types('gear',
                                       inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))



    def test_get_slot_values_THING(self):
        good = "['class_and_instances_as_html', 'frame_as_html']"
        resp = list(get_slot_values(':THING','npt_for_self',
                                    slot_type=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))


    def skip_test_get_slot_values_gear(self):
        good = "['class_and_instances_as_html', 'frame_as_html'," +\
               " web_log_category_as_html', 'web_log_category_self_as_html']"
        resp = list(get_slot_values('web_log_category','npt_for_self',
                                    slot_type=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))


    def test_get_slot_values_in_detail_web_log_category(self):
        good = "[['class_and_instances_as_html', 0, 0]," +\
               " ['frame_as_html', 0, 0]," +\
               " ['web_log_category_as_html', 1, 0]," +\
               " ['web_log_category_self_as_html', 1, 0]]"

        resp = list(get_slot_values_in_detail('web_log_category',
                                              'npt_for_self',
                                              slot_type=Node._all,
                                              kb_local_only_p=0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))
        

    def test_get_slot_values_in_detail_THING(self):
        good = "[['class_and_instances_as_html', 0, 0], ['frame_as_html', 0, 0]]"

        resp = list(get_slot_values_in_detail(':THING',
                                              'npt_for_self',
                                              slot_type=Node._all,
                                              kb_local_only_p=0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_parents(self):
        good = "[PRIMORDIAL_KB, nooron_app_architecture.pykb," +\
               " smurp_web_log_data.pykb, web_log_schema.pykb," +\
               " web_log_skeleton.pykb]"
        resp = current_kb().get_kb_parents()
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))        
        


if __name__ == "__main__":
    unittest.main()
