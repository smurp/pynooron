
from distutils.core import setup

setup(
    name = 'pyokbc',
    version = "0.1.0",
    description = "An implementation of Open Knowledge Base Connectivity",
    author = "Shawn F Murphy",
    author_email = "smurp@smurp.com",
    url = "http://www.noosphere.org/software/pyokbc",

    packages = ['pyokbc','pyokbc.tests'],
    package_dir = {'pyokbc':'.'},
    )
