#! /usr/bin/env python2.1
"""Run all tests."""

import os
import sys
import utils
import unittest
import test_funcs


    
    
if __name__ == "__main__":
    os.environ["LOCAL_CONNECTION_PLACE"] = os.getcwd()
    mykb = open_kb("PeopleData.pykb")
    goto_kb(mykb)
    unittest.main()



"""
    import unittest

    class IntegerArithmenticTestCase(unittest.TestCase):
        def testAdd(self):  ## test method names begin 'test*'
            self.assertEquals((1 + 2), 3)
            self.assertEquals(0 + 1, 1)
        def testMultiply(self);
            self.assertEquals((0 * 10), 0)
            self.assertEquals((5 * 8), 40)

    if __name__ == '__main__':
        unittest.main()

"""
