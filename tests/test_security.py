#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_security.py,v 1.1 2003/03/28 07:31:23 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('..')
sys.path.append('../code')


from OkbcOperation import IPListSecurityEngine 

class nest:
    def __init__(self,thing,name):
        self.__dict__[name] = thing

good_guy = nest(nest(nest(['1.1.1.1'],'addr'),
                     'channel'),
                '_request')

bad_guy = nest(nest(nest(['9.9.9.9'],'addr'),
                    'channel'),
               '_request')

neutral_guy = nest(nest(nest(['5.5.5.5'],'addr'),
                        'channel'),
                   '_request')

class chained_engine(IPListSecurityEngine):
    mess = 'Caught by Chain'
    def denied_p(self,op):
        return self.mess

class IPSecurityTest(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)

    def test_allow_everybody_by_default(self):
        sec_eng = IPListSecurityEngine()        
        self.failIf(sec_eng.denied_p(bad_guy),
                    'failing to allow everybody by default')

    def test_allow_only_listed(self):
        sec_eng = IPListSecurityEngine(allow=['1.1.1.1'],deny=1)

        self.failIf(sec_eng.denied_p(good_guy),
                    'failing to let the know good guys in')

        self.failUnless(sec_eng.denied_p(neutral_guy),
                        'failing to deny others when deny=1')
        

    def test_deny_only_listed(self):
        sec_eng = IPListSecurityEngine(deny=['9.9.9.9'],allow=1)

        self.failIf(sec_eng.denied_p(neutral_guy),
                    'failing to allow neutral guys when allow=1')

        self.failUnless(sec_eng.denied_p(bad_guy),
                        'failing to deny specified bad guys')


    def test_neutral_caught_in_chain(self):
        sec_eng = IPListSecurityEngine(deny=['9.9.9.9'],
                                       chain=chained_engine())

        self.assertEquals(sec_eng.denied_p(neutral_guy),
                          chained_engine.mess,
                          'neutrals not caught in chain')
        

if __name__ == "__main__":
    unittest.main()
    
