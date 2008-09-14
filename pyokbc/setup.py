#!/usr/bin/env python

__version__='$Revision: 1.5 $'[11:-2]
__cvs_id__ ='$Id: setup.py,v 1.5 2008/09/14 16:30:08 smurp Exp $'

from distutils.core import setup

setup(name="PyOKBC",
      version = "0.1.2",
      description = "Python implementation of Open KnowledgeBase Connectivity",
      author = "Shawn F. Murphy",
      author_email = "smurp@smurp.com",
      url = "http://www.noosphere.org/software/pyokbc/",
      packages = ['pyokbc','pyokbc.tests'],
      package_dir = {'pyokbc':'.',
                     'pyokbc.tests':'./tests'},
      package_data = {'pyokbc.tests':['tests/*.pykb']}
      
      )
