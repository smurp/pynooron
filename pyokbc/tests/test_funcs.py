#!/usr/bin/env python

__version__='$Revision: 1.25 $'[11:-2]
__cvs_id__ ='$Id: test_funcs.py,v 1.25 2006/03/21 20:48:06 smurp Exp $'


"""
Most tests will use something like this:

        self.perform_comparison(
            msg    = "",
            expect = set(),
            got    = set())

"""

import os
import sys
import string
import unittest
sys.path.append('../..')
from pyokbc import *
from debug_tools import timed

def str_sort(a,b):
    return cmp(str(a),str(b))

class ReadOnlyTestCase(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
        #addenda = open_kb(create_kb_locator('Addenda'))

    def perform_comparison(self,expect=None,got=None,msg=""):
        msg += "\n  expected: %(expect)s\n   but got: %(got)s"
        self.assertEquals(expect,got,msg % locals())

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
        #self.assertEquals(meta.get_instance_types(locator),[])
        #self.assertEquals(meta.instance_of_p(locator,':KB')[0],True)
        self.failIf(not kb_p(locator))

    def test_0006_find_kb_locator(self):
        #PyOkbc.DEBUG_METHODS.append('find_kb_locator')
        PyOkbc.DEBUG = 0
        PyOkbc.BREAK = 0
        
        locator = find_kb_locator('PeopleData')
        meta = meta_kb()
        self.failIf(not kb_p(locator))        


    def test_0007_open_kb(self):
        locator = find_kb_locator('PeopleData')
        mykb = open_kb(locator)
        self.failIf(not kb_p(mykb))
        self.failIf(not mykb._opened)

    def test_0008_kb_name_is_without_pykb(self):
        kb_name = 'PeopleData'
        peep = find_kb(kb_name)
        self.perform_comparison(
            msg    = "the names of KBs should not get adorned with anything (esp. '.pykb'!)",
            expect = kb_name,
            got    = str(peep))
        
    def test_0009_goto_kb(self):
        meta = meta_kb()
        #simple_dump_kb(meta,skip=['SLOT','FACET','PrimordialKb','KLASS'])
        loc = find_kb_locator("PeopleData")
        peep = find_kb(loc)
        goto_kb(peep)        
        the_kb = current_kb()
        self.failIf(not kb_p(the_kb))
        self.assertEquals(str(the_kb),'PeopleData')
        #self.assertNotEquals(type(the_kb),type(''),'current_kb() returns a string')
        #print the_kb.get_frame_name()


    def test_0010_get_kb_direct_parents(self):
        peeps = find_kb('PeopleData')
        self.perform_comparison(
            msg    = "get_kb_direct_parents() not working, first see test_0008",
            expect = set(['PeopleSchema', 'LiteratureOntology']),
            got    = set(map(str,peeps.get_kb_direct_parents())))


    def test_0011_get_kb_parents(self):
        peeps = find_kb('PeopleData')
        self.perform_comparison(
            msg    = "get_kb_parents() not working, first see test_0008",
            expect = set(['PRIMORDIAL_KB', 'PeopleSchema', 'LiteratureOntology']),
            got    = set(map(str,peeps.get_kb_parents())))


    def test_0014_get_frame_in_kb_documentation(self):
        frame,frame_found_p = get_frame_in_kb(':DOCUMENTATION')
        
        self.failIf(not frame_found_p,'Cannot find :DOCUMENTATION frame')


    def test_0016_documentation(self):
        good = doc="You know, Alice!  With the restaraunt..."
        resp = get_slot_value('AliceLidell',
                              ':DOCUMENTATION', # Node._DOCUMENTATION,
                              slot_type=Node._own)[0]
        if not resp:
            print_frame('AliceLidell')
        self.assertEquals(good, str(resp))


    def test_0018_get_frame_pretty_name(self):
        good = 'Alice in Wonderland'
        resp = get_frame_pretty_name('AliceInWonderland')
        self.assertEquals(good, str(resp))


    def test_0020_get_class_instances(self):
        good = "[CharlesLutwidgeDodgson, SamuelBeckett]"
        resp = list(get_class_instances('AdultHuman')[0])
        resp.sort(str_sort)
        self.assertEquals(good,str(resp))

    def test_0025_inverse(self):
        import pprint
        mykb = find_kb('InverseMinimal')

        alice = mykb.get_frame_in_kb('AliceInWonderland')[0]
        lewis = mykb.get_frame_in_kb('LewisCarroll')[0]
        glass = mykb.get_frame_in_kb('ThroughTheLookingGlass')[0]

        self.perform_comparison(
            msg    = "basic slot-value assertions disturbed by inverse",
            expect = set([str(alice),str(glass)]),
            got    = set(list(mykb.get_slot_values('LewisCarroll','Wrote', kb_local_only_p = 0)[0])))

        self.perform_comparison(
            msg    = "basic :SLOT-INVERSE functionality broken",
            expect = set([lewis]),
            got    = set(list(mykb.get_slot_values('AliceInWonderland','WrittenBy', kb_local_only_p = 0)[0])))

        self.perform_comparison(
            msg    = "perhaps there is a wrong number of _inverse_values stored?",
            expect = set([lewis]),
            got    = set(alice._inverse_slots.get('WrittenBy')))
            
        self.perform_comparison(
            msg = "_inverse_slots do not merge right?",
            expect = set([mykb.get_frame_in_kb('JohnVonNeumann')[0],
                          mykb.get_frame_in_kb('OskarMorgenstern')[0]]),
            got = set(mykb.get_slot_values('TheoryOfGamesandEconomicBehaviour','WrittenBy')[0]))
                          
        self.perform_comparison(
            msg    = "Node should be __eq__ to their frame name as a string",
            expect = 'AliceInWonderland',
            got    = alice)
        
        self.perform_comparison(
            msg    = "inverse values are not equal to forward values",
            expect = set(map(str,[alice,glass])),
            got    = set(list(mykb.get_slot_values('LewisCarroll','Wrote', kb_local_only_p = 0)[0])))


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

    def test_0060_get_frame_slots_direct(self):
        good = "['Age', 'BirthTime', 'Eats', 'Wrote']"
        #print_frame('SamuelBeckett')
        fs = get_frame_slots('SamuelBeckett',
                             inference_level=Node._direct)[0]
        #print 'SamuelBeckett.get_frame_slots(direct)  =',fs        
        resp = list(fs)
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0065_get_frame_slots_all(self):
        orig_kb = current_kb()
        mykb = find_kb('Addenda')
        #print mykb,type(mykb),mykb.__class__.__name__
        self.failIf(not kb_p(mykb),'No kb Addenda')

        #import epdb;     p = epdb.Epdb();     p.set_trace()        
        good = "['Age', 'BirthTime', 'Eats', 'Friend'," + \
               " 'Speaks', 'Species', 'Wrote']"
        goto_kb(mykb)
        self.assertEquals(current_kb(),mykb)
        fs = get_frame_slots('SamuelBeckett',#kb=mykb,
                             slot_type=Node._all,
                             inference_level=Node._all)[0]
        #print 'SamuelBeckett.get_frame_slots(all)  =',fs
        resp = list(fs)
        goto_kb(orig_kb)
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))


    def test_0070_get_frame_slots_taxonomic(self):
        good = "['Age', 'BirthTime', 'Eats', 'Speaks', 'Species', 'Wrote']"
        resp = list(get_frame_slots('SamuelBeckett',
                                    inference_level=Node._taxonomic)[0])
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def test_0090_get_kb_direct_parents(self):
        good = "[LiteratureOntology, PeopleSchema]"
        resp = list(get_kb_direct_parents())
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))

    def PASS_test_0100_get_kb_frames(self):
        """
        Really, this test shows a problem with the ontologies because
        Wrote appears in both LiteratureOntology.pykb and PeopleSchema.pykb

        Anyway, should get_kb_frames return two frames of the same name
        if they happen to appear in two different kbs?  I'd say yes!

        """
        
        resp = list(get_kb_frames(kb_local_only_p=0))
        resp.sort(str_sort)
        unique = {}
        dupes = {}
        there_were_dupes = 0
        for frame in resp:
            #if not unique.has_key(str(frame)):
            l = unique.setdefault(str(frame),[])
            if l <> []:
                there_were_dupes =+ 1
                dupes[str(frame)] = 1
            l.append(frame)
        #print "lengths",len(resp), len(unique.keys())
        for f in resp:
            u = unique[str(f)]
            if len(u) > 1:
                if not eql(u[0],u[1]):
                    print u[0].__dict__                    
                    print "----------------------------"
                    print u[1].__dict__
                    #print get_frame_details(u[1],kb=u[1]._kb)
                self.failIf(not eql(u[0],u[1]),
                            "get_kb_frames() has duplicates AND not eql(%s)"%str(u))

        self.failIf(there_were_dupes,
                    'duplicates frames: ' + str(','.join(dupes.keys())))

    def test_0110_get_kb_frames_klop(self):
        good = "[AliceInWonderland, AliceLidell," + \
               " CharlesLutwidgeDodgson, ChristopherRobin," + \
               " DeathTime, LewisCarroll, SamuelBeckett]"
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

        otherpeople = open_kb(create_kb_locator('OtherPeople'))
        self.assertEquals(kb_p(otherpeople),True)        

        children = get_kb_direct_children(ontology)
        self.failIf(len(children) < 1,"get_kb_direct_children() failing")
        parent = []
        for kb in children:
            kb.get_kb_direct_parents()
            parent.append(kb.get_kb_direct_parents()[0])
        #print "PARENTS =",parent
        for p in parent:
            self.assertEquals(p,parent[0],"the kb '%s' is duplicated" % p)
        self.failIf(len(parent) < 1,
                    'something wrong with get_kb_direct_parents()')
            

    def test_0145_test_get_kb_direct_children(self):
        schema = find_kb('PeopleSchema')
        good = "[OtherPeople, PeopleData]"
        resp = list(get_kb_direct_children(schema))
        resp.sort(str_sort)
        self.assertEquals(good, str(resp))


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
