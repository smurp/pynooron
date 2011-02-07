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
                  kr_root+'apps_of/pod',
                  kr_root+'nooron_apps',
                  kr_root+'nooron_foundations',
                  cwd+'/../../know']
        
        os.environ["LOCAL_CONNECTION_PLACE"] = string.join(places,':')
        #std_tranny = open_kb("standard_transmission_fsa")
        mykb = open_kb(meta_kb())
        goto_kb(mykb)


    def SKIP_test_0001_what_is_breaking_auto_create_links(self):
        goto_kb(meta_kb())
        ckb = current_kb()
        self.assertEquals(meta_kb(),ckb,"%s should really be %s" % (ckb,meta_kb()))
        self.assertNotEquals(type(ckb),str,
                             'the meta_kb should not be of type %s for gods sake' % \
                                 type(ckb))
        self.assertEquals(str(ckb),'doh')
        count = 0
        nooron_app_classes = get_class_instances('nooron_app_class')[0]
        self.assertNotEquals(nooron_app_classes,[],
                             'nooron_app_classes should not be []')
        for inst in nooron_app_classes:
            count += 1
            self.assertNotEquals(type(inst),str,
                                 "'%s' should not be a %s" % (inst,type(inst)))
        self.assertNotEquals(0,0,"oh, there were no instances of 'nooron_app_class'")
        for inst in get_class_instances('nooron_app_class')[0]:
            count += 1
            self.assertNotEquals(type(inst),str,
                                 "'%s' should not be a %s" % (inst,type(inst)))
        self.assertNotEquals(0,0,"oh, there were no instances of 'nooron_app_class'")

    def SKIP_test_0020_doubled_links_in_best_practices(self):
        bp = open_kb('best_practices')
        
        self.perform_comparison(
            msg    = "wrong values for BeEfficient.MoreGeneralPractice",
            expect = set(['StayInFlow']),
            got    = set(bp.get_slot_values('BeEfficient','MoreGeneralPractice')[0]),)
        self.perform_comparison(
            msg    = "wrong values for BeEfficient.MoreSpecificPractice",
            expect = set(['BeEfficient']),
            got    = set(bp.get_slot_values('StayInFlow','MoreSpecificPractice')[0]),)

    def test_0030_pattern_language_criteria(self):
        #npl = open_kb('nooron_pattern_language')
        npl = open_kb('nooron_app_architecture')

        universal_criteria = set(['Critique', 'ClarityOfExpression', 'Endorsement'])
        dom_of_pert = npl.get_slot_value('hasPertinentCriteria',':DOMAIN')[0]
        self.perform_comparison(
            msg    = "Why does %(dom_of_pert)s have no criteria" % locals(),
            expect = universal_criteria,
            got    = set_of_strings(npl.get_slot_values(dom_of_pert,
                                                        'hasPertinentCriteria',)[0]))

        sub_of_dom_of_pert = ":KB"
        self.perform_comparison(
            msg    = "Hmm.  I thought %(sub_of_dom_of_pert)s was a subclass of %(dom_of_pert)s" % locals(),
            expect = set([str(dom_of_pert)]),
            got    = set_of_strings(npl.get_class_superclasses(sub_of_dom_of_pert)[0]))
        self.perform_comparison(
            msg    = str("%(sub_of_dom_of_pert)s is a subclass of %(dom_of_pert)s " +\
                             "then why does %(sub_of_dom_of_pert)s not have %(dom_of_pert)s's criteria?") % locals(),
            expect = universal_criteria,
            got    = set_of_strings(npl.get_slot_values(sub_of_dom_of_pert,
                                                          'hasPertinentCriteria',)[0]))

    def test_0040_universal_evaluations(self):
        naa = open_kb('nooron_app_architecture')
        dom_of_pert = naa.get_slot_value('hasPertinentCriteria',':DOMAIN')[0]
        the_eval = naa.get_class_instances('Evaluation')[0][0]

        self.perform_comparison(
            msg    = "What is the subject of %(the_eval)s" % locals(),
            expect = set(['HasVisibility_Critique_ShawnFrancisMurphy']),
            got    = set([str(the_eval)]))

        self.perform_comparison(
            msg    = "What is the subject of %(the_eval)s" % locals(),
            expect = set(['HasVisibility']),
            got    = set(get_slot_value(the_eval,'SubjectOfEvaluation')[0]),)
                

if __name__ == "__main__":
    unittest.main()
    
