#!/usr/bin/env python
"""Run all tests."""

import os
import sys
import unittest
from test_funcs import *
from test_primordial import *
from test_PyKb import *
from test_BrainKb import *
from test_fs_connection import *

if __name__ == "__main__":
    unittest.main(verbosity=os.environ.get('VERBOSE',0))
    print "to see details:"
    print "   VERBOSE=1 ./run.py"


