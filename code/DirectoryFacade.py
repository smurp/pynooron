
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: DirectoryFacade.py,v 1.2 2002/08/02 18:47:18 smurp Exp $'

import os

class DirectoryFacade:
    def __init__(self,path):
        self._path = path

    def objectValues(self):
        lst = os.listdir(self._path)
        lst.sort()
        for indx in range(len(lst)):
            i = lst[indx]
            #if self.filesystem.isdir(self._path + i):
            #    lst[indx] = i + "/"
        return lst
