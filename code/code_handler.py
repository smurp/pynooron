
__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: code_handler.py,v 1.1 2002/07/18 20:44:36 smurp Exp $'


"""Serve up the /code/ directory as described at 
   http://www.noosphere.org/discuss/zwiki/Nooron"""

import string
from medusa import default_handler

class code_handler(default_handler.default_handler):
    def match(self,request):
        path = request.split_uri()[0]
        indx = string.find(path,self.filesystem.wd)
        print path, self.filesystem.wd,indx,self.filesystem.isdir(path)

        return indx != 0

