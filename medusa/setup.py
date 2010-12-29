
__revision__ = '$Id: setup.py,v 1.8 2002/08/20 17:35:35 akuchling Exp $'

from distutils.core import setup

setup(
    name = 'medusa',
    version = "0.5.3",
    description = "A framework for implementing asynchronous servers.",
    author = "Sam Rushing",
    author_email = "rushing@nightmare.com",
    maintainer = "A.M. Kuchling",
    maintainer_email = "akuchlin@mems-exchange.org",
    url = "http://oedipus.sourceforge.net/medusa/",

    packages = ['medusa'],
    package_dir = {'medusa':'.'},
    )
