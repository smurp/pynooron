#!/usr/bin/env python

from distutils.core import setup

setup(name="Nooron",
      version = "0.2.10",
      description = "a distributed eco-system of knowledge, logic and presentation",
      author = "Shawn F. Murphy",
      author_email = "smurp@smurp.com",
      url = "http://www.nooron.org/",
      packages = ['nooron'],
      scripts = ['scripts/localhost.py'],
      package_dir = {'nooron':           'code',
                     'nooron.templates': 'templates'},
      package_data = {'nooron.templates':
                          ['templates/*.html',
                           'templates/*.dot',
                           'templates/*.dbk',
                           'templates/form_master',
                           'templates/favicon.ico',
                           ]},
      )
