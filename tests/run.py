#!/usr/bin/env python
"""Run all tests."""

import os
import sys
import unittest
from test_pyokbc import *
from test_okbcop import *
#from test_security import *
from test_CachingPipeliningProducer import *

if __name__ == "__main__":
    unittest.main()

