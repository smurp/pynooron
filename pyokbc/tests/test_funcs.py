#!/usr/bin/env python2.1

__version__='$Revision: 1.10 $'[11:-2]
__cvs_id__ ='$Id: test_funcs.py,v 1.10 2002/11/11 22:47:18 smurp Exp $'

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
        addenda = open_kb("Addenda.pykb")
        mykb = open_kb("OtherPeople.pykb")
        mykb = open_kb("PeopleData.pykb")
        goto_kb(mykb)

    def test_get_class_instances(self):
        good = "[CharlesLutwidgeDodgson, SamuelBeckett]"
        resp = list(get_class_instances('AdultHuman')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))
        
    def test_get_class_superclasses(self):
        resp = list(get_class_superclasses('AdultHuman')[0])
        resp.sort(str_sort)
        good = "[:THING, Agent, Animal, Human, Mammal, Primate]"
        self.assertEquals(good,str(resp))

    def test_get_frame_sentences(self):
        good = \
             """(individual SamuelBeckett)\n""" + \
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

    def test_get_frame_slots_all(self):
        mykb = find_kb('Addenda.pykb')
        #mykb = current_kb()
        good = "['Age', 'BirthTime', 'Eats', 'Friend'," + \
               " 'Speaks', 'Species', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',kb=mykb,
                                    slot_type=Node._all,
                                    inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_frame_slots_direct(self):
        good = "['Age', 'BirthTime', 'Eats', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',
                                    inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_frame_slots_taxonomic(self):
        good = "['Age', 'BirthTime', 'Eats', 'Speaks', 'Species', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',
                                    inference_level=Node._taxonomic)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_direct_children(self):
        schema = find_kb('PeopleSchema.pykb')
        good = "[OtherPeople.pykb, PeopleData.pykb]"
        resp = list(get_kb_direct_children(schema))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_direct_parents(self):
        good = "[LiteratureOntology.pykb, PRIMORDIAL_KB, PeopleSchema.pykb]"
        resp = list(get_kb_direct_parents())
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_frames(self):
        good = 78
        resp = list(get_kb_frames(kb_local_only_p=0))
        self.assertEquals(good,len(resp))

    def test_get_kb_frames_klop(self):
        good = "[AliceInWonderland, AliceLidell," + \
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " LewisCarroll, SamuelBeckett]"
        resp = list(get_kb_frames(kb_local_only_p=1))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_individuals(self):
        good = "[AliceInWonderland, AliceLidell," +\
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " English, LewisCarroll, SamuelBeckett]"
        resp = list(get_kb_individuals())
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_individuals_klop(self):
        good = "[AliceInWonderland, AliceLidell," +\
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " LewisCarroll, SamuelBeckett]"
        resp = list(get_kb_individuals(kb_local_only_p=1))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_kb_parents_REUSE(self):
        ontology = find_kb('PeopleSchema.pykb')
        children = get_kb_direct_children(ontology)
        parent = []
        for kb in children:
            parent.append(get_kb_direct_parents(kb)[0])
        self.assertEquals(parent[0],parent[1])

    def test_get_instance_types_all(self):
        mykb = find_kb('Addenda.pykb')        
        good = '[:THING, AdultHuman, Agent, Animal, Human, Mammal, Primate]'
        resp = list(get_instance_types('SamuelBeckett',
                                       kb = mykb,
                                       inference_level=Node._all)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_direct(self):
        good = '[AdultHuman]'
        resp = list(get_instance_types('SamuelBeckett',
                                       inference_level=Node._direct)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_instance_types_taxonomic(self):
        good = '[:THING, AdultHuman, Agent, Animal, Human, Mammal, Primate]'
        resp = list(get_instance_types('SamuelBeckett',
                                       inference_level=Node._taxonomic)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def skip_test_get_slot_facets(self):
        good = ""
        resp = list(get_slot_facets('SamuelBeckett','')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))

    def test_get_slot_value(self):
        good = """83"""
        resp = get_slot_value('SamuelBeckett','Age',
                              slot_type=Node._own)[0]
        self.assertEquals(good, str(resp))

    def test_get_slot_values(self):
        mykb = find_kb('Addenda.pykb')
        good = """['MorePricksThanKicks', 'Murphy', 'WaitingForGodot']"""
        resp = list(mykb.get_slot_values('SamuelBeckett','Wrote',
                                         kb_local_only_p = 0)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_slot_values_klop(self):
        mykb = find_kb('Addenda.pykb')
        good = """['MorePricksThanKicks', 'Murphy']"""
        resp = list(mykb.get_slot_values('SamuelBeckett','Wrote',
                                         kb_local_only_p = 1)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_slot_values_all(self): # bugged
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
        

    def test_get_slot_values_all_klop(self):
        good = "['Apple', 'Berry', 'Cookie']"
        resp = list(get_slot_values('SamuelBeckett','Eats',
                                    slot_type=Node._all,
                                    kb_local_only_p=1)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_get_slot_values_own(self):
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

    def test_get_slot_values_template(self): # bugged
        good = """['DairyProducts', 'Grains', 'Meats', 'Vegetables']"""
        resp = list(get_slot_values('SamuelBeckett','Eats',
                                    slot_type=Node._template)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_documentation(self):
        good = doc="You know, Alice!  With the restaraunt..."
        resp = get_slot_value('AliceLidell',Node._DOCUMENTATION,
                              slot_type=Node._own)[0]
        self.assertEquals(good, str(resp))

    def test_stayup(self):
        first = len(get_class_instances('Human')[0])
        second = len(get_class_instances('Human')[0])        
        self.assertEquals(first,second)


if __name__ == "__main__":
    unittest.main()
