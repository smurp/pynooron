
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
