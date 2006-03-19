#!/usr/bin/env python

__version__='$Revision: 1.23 $'[11:-2]
__cvs_id__ ='$Id: test_funcs.py,v 1.23 2006/03/19 16:55:16 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *

def str_sort(a,b):
    return cmp(str(a),str(b))

class ReadOnlyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        #addenda = open_kb(create_kb_locator('Addenda'))
        print """



        """

    def test_0003_connection(self):
        con = local_connection()
        #PyOkbc.DEBUG_METHODS.append('get_kbs')
        #PyOkbc.BREAK = 1
        #PyOkbc.DEBUG = 0        
        #print "OH MY GOD"
        self.assertNotEquals(type(con),type(''))
        self.assertEquals(con.__class__.__name__,'FileSystemConnection')

    def test_0005_create_kb_locator(self):
        locator = create_kb_locator('PeopleData')
        meta = meta_kb()
        
        #print "meta    =",type(meta),   meta.__class__.__name__
        #print "locator =",type(locator),locator.__class__.__name__
        #self.assertEquals(meta.get_instance_types(locator),[])
        self.assertEquals(meta.instance_of_p(locator,':KB_LOCATOR')[0],True)


    def test_0006_find_kb_locator(self):
        #PyOkbc.DEBUG_METHODS.append('find_kb_locator')
        PyOkbc.DEBUG = 0
        PyOkbc.BREAK = 0
        
        locator = find_kb_locator('PeopleData')
        meta = meta_kb()
        self.assertEquals(meta.instance_of_p(locator,':KB_LOCATOR')[0],True)
        self.assertEquals(meta.get_slot_value(locator,'filename')[0],
                          'PeopleData.pykb')

    def test_0007_open_kb(self):
        #PyOkbc.DEBUG_METHODS.append('open_kb')
        #PyOkbc.DEBUG_METHODS.append('get_frame_in_kb_internal')        
        #PyOkbc.BREAK = 0
        #PyOkbc.DEBUG = 0        

        locator = find_kb_locator('PeopleData')

        meta = meta_kb()        
        #simple_dump_kb(meta,skip=['SLOT','FACET','PrimordialKb','KLASS'])

        mykb = open_kb(locator,connection=local_connection())
        #print mykb._v_store.keys()
        PyOkbc.BREAK = 0
        #simple_dump_kb(meta,skip=['SLOT','FACET','PrimordialKb','KLASS'])
        self.assertNotEquals(type(mykb),type(''))





    def test_0008_goto_kb(self):
        meta = meta_kb()
        #simple_dump_kb(meta,skip=['SLOT','FACET','PrimordialKb','KLASS'])
        loc = find_kb_locator("PeopleData")
        #print meta.print_frame(loc)
        #peep = find_kb(loc)
        PyOkbc.BREAK = 0        
        peep = find_kb('PeopleData')
        goto_kb(peep)        
        the_kb = current_kb()
        self.failIf(not kb_p(the_kb))
        locator_names = meta._v_store.keys()
        locator_names.sort()
        self.assertEquals(locator_names,
                          ['LiteratureOntology', 'PeopleData', 'PeopleSchema'])
        self.assertEquals(str(the_kb),'PeopleData')
        #self.assertNotEquals(type(the_kb),type(''),'current_kb() returns a string')
        #print the_kb.get_frame_name()



    def test_0010_documentation(self):
        good = doc="You know, Alice!  With the restaraunt..."
        #print "current_kb",current_kb()        
        #goto_kb("PeopleData")
        #print "current_kb",current_kb()
        #print "direct_parents",get_kb_direct_parents()
        #print "AliceLidell",get_frame_details('AliceLidell')
        #print "Child instances",get_class_instances('Child')[0]
        
        resp = get_slot_value('AliceLidell',
                              ':DOCUMENTATION', # Node._DOCUMENTATION,
                              slot_type=Node._own)[0]
        self.assertEquals(good, str(resp))


    def test_0020_get_class_instances(self):
        good = "[CharlesLutwidgeDodgson, SamuelBeckett]"
        resp = list(get_class_instances('AdultHuman')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))


    def test_0030_get_class_superclasses(self):
        resp = list(get_class_superclasses('AdultHuman')[0])
        resp.sort(str_sort)
        good = "[:THING, Agent, Animal, Human, Mammal, Primate]"
        self.assertEquals(good,str(resp))

    def test_0040_get_class_subclasses(self):
        resp = list(get_class_subclasses('Agent')[0])
        resp.sort(str_sort)
        good = "[AdultHuman, Child, Human]"
        self.assertEquals(good,str(resp))

    def test_0050_get_frame_details(self):
        good = 738
        resp = get_frame_details('SamuelBeckett')[0]
        str_resp = str(resp)
        #print resp
        len_str_resp = len(str(resp))
        #print resp
        ## FIXME this 738 nonsense needs analysis
        self.assertEquals(good,len_str_resp)
        num_keys = len(resp.keys())
        #print resp.keys()
        self.assertEquals(9,num_keys)

    def test_0055_get_frame_sentences(self):
        good = \
             """(individual SamuelBeckett)\n""" + \
             """(instance-of SamuelBeckett :INDIVIDUAL)\n""" + \
             """(instance-of SamuelBeckett AdultHuman)\n""" + \
             """(slot Age SamuelBeckett 83)\n""" + \
             """(slot BirthTime SamuelBeckett "1906-04-13 GMT")\n""" + \
             """(slot Eats SamuelBeckett "Apple")\n""" + \
             """(slot Eats SamuelBeckett "Berry")\n""" + \
             """(slot Eats SamuelBeckett "Cookie")\n""" + \
             """(slot Wrote SamuelBeckett "WaitingForGodot")"""
        resp = list(get_frame_sentences('SamuelBeckett')[0])
        resp.sort()
        self.assertEquals(good, string.join(resp,"\n"))

    def test_0060_get_frame_slots_all(self):
        mykb = find_kb('Addenda')
        #mykb = current_kb()
        good = "['Age', 'BirthTime', 'Eats', 'Friend'," + \
               " 'Speaks', 'Species', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',kb=mykb,
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0060_get_frame_slots_direct(self):
        good = "['Age', 'BirthTime', 'Eats', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',
                                    inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0070_get_frame_slots_taxonomic(self):
        good = "['Age', 'BirthTime', 'Eats', 'Speaks', 'Species', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',
                                    inference_level=Node._taxonomic)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_0080_test_get_kb_direct_children(self):
        schema = find_kb('PeopleSchema')
        good = "[OtherPeople, PeopleData]"
        resp = list(get_kb_direct_children(schema))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0090_get_kb_direct_parents(self):
        good = "[LiteratureOntology, PRIMORDIAL_KB, PeopleSchema]"
        resp = list(get_kb_direct_parents())
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0100_get_kb_frames(self):
        good = 94
        resp = list(get_kb_frames(kb_local_only_p=0))
        self.assertEquals(good,len(resp))

#class Bogus:
    def test_0110_get_kb_frames_klop(self):
        good = "[AliceInWonderland, AliceLidell," + \
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " LewisCarroll, SamuelBeckett]"
        resp = list(get_kb_frames(kb_local_only_p=1))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0120_get_kb_individuals(self):
        good = "[AliceInWonderland, AliceLidell," +\
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " English, LewisCarroll, SamuelBeckett]"
        resp = list(get_kb_individuals())
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0130_get_kb_individuals_klop(self):
        good = "[AliceInWonderland, AliceLidell," +\
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " LewisCarroll, SamuelBeckett]"
        resp = list(get_kb_individuals(kb_local_only_p=1))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0133_get_kbs(self):
        kbs = meta_kb().get_kbs()
        self.assertEquals(kbs,'not sure yet')

    def test_0135_get_kb_parents(self):
        peeps = find_kb('PeopleData')
        self.assertEquals(kb_p(peeps),True)
        parents = get_kb_direct_parents(peeps)
        self.failIf(len(parents) <= 1)

    def test_0140_get_kb_parents_REUSE(self):
        """
        Ensure that if a kb is in use more than once, it is
        reused rather than duplicated.  See if the multiple
        child kbs are being duly registered.

        """
        ontology = find_kb('PeopleSchema')
        self.assertEquals(kb_p(ontology),True)
        #meta_kb().print_frame(ontology)
        children = get_kb_direct_children(ontology)
        self.failIf(len(children) < 1,"get_kb_direct_children() failing")
        parent = []
        for kb in children:
            parent.append(kb.get_kb_direct_parents()[0])
        self.assertEquals(parent[0],parent[1])

    def test_0150_get_instance_types_all_SamuelBeckett(self):
        mykb = find_kb('Addenda')        
        good = '[:INDIVIDUAL, :THING, AdultHuman, Agent, Animal,' +\
               ' Human, Mammal, Primate]'
        resp = list(get_instance_types('SamuelBeckett',
                                       kb = mykb,
                                       inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0160_get_instance_types_direct(self):
        good = '[:INDIVIDUAL, AdultHuman]'
        resp = list(get_instance_types('SamuelBeckett',
                                       inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0170_get_instance_types_taxonomic(self):
        good = '[:INDIVIDUAL, :THING, AdultHuman, Agent,' + \
               ' Animal, Human, Mammal, Primate]'
        resp = list(get_instance_types('SamuelBeckett',
                                       inference_level=Node._taxonomic)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_0180_test_get_slot_facets(self):
        good = ""
        resp = list(get_slot_facets('SamuelBeckett','')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))

    def test_0190_get_slot_value(self):
        good = """83"""
        resp = get_slot_value('SamuelBeckett','Age',
                              slot_type=Node._own)[0]
        self.assertEquals(good, str(resp))

    def test_0195_open_kb_via_create_kb_locator(self):
        locator = create_kb_locator('Addenda')
        mykb = open_kb(locator)
        self.failIf(not kb_p(mykb),
                    "Can not open_kb(create_kb_locator('Addenda'))")


    def test_0195_open_kb_via_find_kb_locator(self):
        locator = find_kb_locator('Addenda')
        mykb = open_kb(locator)
        self.failIf(not kb_p(mykb),
                    "Can not open_kb(create_kb_locator('Addenda'))")


    def test_0197_find_kb_by_name(self):
        mykb = find_kb('Addenda')
        self.failIf(not kb_p(mykb),
                    "Can not find_kb('Addenda')")



    def test_0200_get_slot_values(self):
        mykb = find_kb('Addenda')
        self.failIf(not kb_p(mykb), "Can not find_kb('Addenda')")
        good = """['MorePricksThanKicks', 'Murphy', 'WaitingForGodot']"""
        resp = list(mykb.get_slot_values('SamuelBeckett','Wrote',
                                         kb_local_only_p = 0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0210_get_slot_values_klop(self):
        mykb = find_kb('Addenda')
        good = """['MorePricksThanKicks', 'Murphy']"""
        resp = list(mykb.get_slot_values('SamuelBeckett','Wrote',
                                         kb_local_only_p = 1)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0220_get_slot_values_all(self): # bugged
        PyOkbc.DEBUG_METHODS.append('get_slot_values_in_detail_internal')
        PyOkbc.DEBUG = 0

        good = "['Apple', 'Berry', 'Cookie', 'DairyProducts', " + \
               "'Grains', 'Meats', 'Vegetables']"
        resp = list(get_slot_values('SamuelBeckett','Eats',
                                    slot_type=Node._all,
                                    kb_local_only_p=0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))
        PyOkbc.DEBUG = 0

        good = """['English']"""
        resp = list(get_slot_values('SamuelBeckett','Speaks',
                                    slot_type=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))
        

    def test_0230_get_slot_values_all_klop(self):
        good = "['Apple', 'Berry', 'Cookie']"
        resp = list(get_slot_values('SamuelBeckett','Eats',
                                    slot_type=Node._all,
                                    kb_local_only_p=1)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0240_get_slot_values_own(self):
        good = """['Apple', 'Berry', 'Cookie']"""
        resp = list(get_slot_values('SamuelBeckett','Eats',
                                    slot_type=Node._own)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

        good = """[]"""
        resp = list(get_slot_values('SamuelBeckett','Speaks',
                                    slot_type=Node._own)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0250_get_slot_values_template(self): # bugged
        good = """['DairyProducts', 'Grains', 'Meats', 'Vegetables']"""
        resp = list(get_slot_values('SamuelBeckett','Eats',
                                    slot_type=Node._template)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0260_open_kb_without_extension(self):
        good = 'MergeKB'
        merge_kb = open_kb('MergeKB')
        self.failIf(len(merge_kb.get_kb_direct_parents()) < 2,
                    "open_kb() opened a trivial, maybe blank, kb")

    def skip_0270_test_stayup(self):
        # this was to check for one of those no-recursion-setup bugs
        first = len(get_class_instances('gear')[0])
        second = len(get_class_instances('gear')[0])        
        self.assertEquals(first,second)


if __name__ == "__main__":
    unittest.main()
