#!/usr/bin/env python

from distutils.core import setup

setup(
   name = 'ZopePageTemplates',
   maintainer = 'Kevin Smith',
   maintainer_email = 'Kevin.Smith@theMorgue.org',
   description = 'Zope Page Templates',

   extra_path = 'ZopePageTemplates',
   packages = ['.','TAL','ZTUtils'],
)
