#!/usr/bin/env python2.1

__version__='$Revision: 1.11 $'[11:-2]
__cvs_id__ ='$Id: test_pyokbc.py,v 1.11 2003/01/20 14:54:08 smurp Exp $'

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
        mykb = open_kb("smurp_web_log")
        goto_kb(mykb)

    def test_get_class_instances_of_marvel(self):
        good = "[wle_0001, wle_0002]"
        resp = list(get_class_instances('marvel')[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_class_instances_of_web_log_entry(self):
        good = "[wle_0001, wle_0002, wle_0003, wle_0004, wle_0005]"
        resp = list(get_class_instances('web_log_entry')[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_class_superclasses_of_web_log_app(self):
        #good = "[:THING]"
        good = "[:KB, :THING, nooron_app_component, nooron_app_instance]"
        resp = list(get_class_superclasses('web_log_app')[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_class_superclasses_of_web_log_app_in_blog_ontology(self):
        kb = find_kb('web_log_ontology')
        good = "[:KB, :THING, nooron_app_component, nooron_app_instance]"
        resp = list(get_class_superclasses('web_log_app',kb=kb)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))
        

    def test_get_frame_slots_all_gear(self):
        good = "[':DOCUMENTATION', 'actions_for_instances'," +\
               " 'npt_for_instances'," + \
               " 'npt_for_self', 'slot_display_order']"
        resp = list(get_frame_slots('web_log_category',
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_frame_slots_all_nooron_faq(self):
        nooron_faq = find_kb('nooron_faq')
        good = "[':DOCUMENTATION', 'npt_for_self', 'slot_display_order']"
        resp = list(get_frame_slots(nooron_faq,
                                    kb=nooron_faq,
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))    

    def test_get_frame_slots_all_web_log_category(self):
        good = "[':DOCUMENTATION', 'actions_for_instances'," +\
               " 'npt_for_instances'," + \
               " 'npt_for_self', 'slot_display_order']"
        resp = list(get_frame_slots('web_log_category',
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_frame_slots_all_THING(self):
        good = "[':DOCUMENTATION', 'npt_for_self']"
        resp = list(get_frame_slots(':THING',
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_transform_dot_2_ps(self):
        good = "[:INDIVIDUAL, :THING, ExternalCommand, NooronTransformer]"
        resp = list(get_instance_types('transform_dot_2_ps')[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_gear(self):
        good = "[:CLASS, :THING, web_log_category]"
        resp = list(get_instance_types('gear',
                                       inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_smurp_web_log(self):
        good = "[web_log_app]"
        resp = list(get_instance_types(current_kb(),
                                       inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_wle_0003(self):
        good = "[:INDIVIDUAL, gear, web_log_entry]"
        resp = list(get_instance_types('wle_0003',
                                       inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_kb_parents(self):
        good = "[PRIMORDIAL_KB, convenience_procedures," + \
               " nooron_app_architecture," +\
               " smurp_web_log_data, transformer_ontology," + \
               " web_log_ontology," +\
               " web_log_wardrobe]"
        resp = current_kb().get_kb_parents()
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))        
        
    def test_get_slot_values_THING(self):
        good = "['class_and_instances.html'," +\
               " 'class_and_subclasses.html'," +\
               " 'frame.html']"

        good = "['frame.html'," +\
               " 'frame_details.html']"
        resp = list(get_slot_values(':THING','npt_for_self',
                                    slot_type=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_slot_values_gear(self):
        good = "['class_and_instances_as_html'," +\
               " 'class_and_subclasses_as_html', 'frame_as_html'," +\
               " web_log_category_as_html', 'web_log_category_self_as_html']"
        resp = list(get_slot_values('web_log_category','npt_for_self',
                                    slot_type=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_slot_values_kb_documentation(self):
        good = ""
        resp = list(get_slot_values(current_kb(),':DOCUMENTATION',
                                    slot_type=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_slot_values_in_detail_THING(self):
        good = "[['frame.html', 0, 0]," + \
               " ['frame_details.html', 0, 0]]"
        resp = list(get_slot_values_in_detail(':THING',
                                              'npt_for_self',
                                              slot_type=Node._all,
                                              kb_local_only_p=0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_slot_values_in_detail_web_log_category(self):
        good = "[['class_and_instances_as_html', 0, 0]," +\
               " ['class_and_subclasses_as_html', 0, 0]," +\
               " ['frame_as_html', 0, 0]," +\
               " ['web_log_category_as_html', 1, 0]," +\
               " ['web_log_category_self_as_html', 1, 0]]"
        good = "[['frame_as_html', 0, 0]," +\
               " ['frame_details_as_html', 0, 0]," +\
               " ['web_log_category_as_html', 1, 0]," +\
               " ['web_log_category_self_as_html', 1, 0]]"

        resp = list(get_slot_values_in_detail('web_log_category',
                                              'npt_for_self',
                                              slot_type=Node._all,
                                              kb_local_only_p=0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_class_subclasses_web_log_category(self):
        PyOkbc.DEBUG = 1
        #PyOkbc.DEBUG_METHODS.append('get_class_subclasses')
        PyOkbc.DEBUG_METHODS.append('get_class_subclasses_internal')
        PyOkbc.DEBUG_METHODS.append('get_instance_types_recurse')        
        good = ""
        resp = list(get_class_subclasses('web_log_category')[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))
        PyOkbc.DEBUG = 0

    def skip_test_npts_for_self_and_instances_by_parentage(self):
        nooron_faq = find_kb('nooron_faq')
        proc = get_procedure('npts_for_self_and_instances_by_parentage',
                             kb=nooron_faq)
        luggage = call_procedure(proc,kb=nooron_faq,
                                 arguments=[['web_log_app'],None])
        print len(luggage)
        print luggage

    def test_get_class_superclasses_of_faq_app_directly(self):
        nooron_faq = find_kb('nooron_faq')        
        good = "[:THING, nooron_app_instance]"
        resp = list(get_class_superclasses('faq_app',
                                           kb=nooron_faq,
                                           inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))
        

if __name__ == "__main__":
    unittest.main()
    
