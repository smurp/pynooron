
__version__='$Revision: 1.3 $'[11:-2]
__cvs_id__ ='$Id: NooronRoot.py,v 1.3 2002/07/29 22:37:50 smurp Exp $'

"""
NooronRoot is the root object of a nooron instance.

It is a singleton. Or rather a Borg:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531

"""
import os
from TemplateManager import TemplateManager

class NooronRoot:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__dict__.has_key('prepped'):
            self._template_root = TemplateManager(self,'templates')
            self.__dict__['prepped'] = 1
            self.__dict__['trout'] = 'booger'
            
    fsroot = None
    http_server = None
    pipeline_factory = None

    def make_fname(self,frag):
        if type(frag) == type([]):
            frag = os.path.join(frag[0],frag[1])
        return os.path.join(self.fsroot,frag)
    
    def template_root(self):
        return self._template_root


if __name__ == "__main__":
    nooron1 = NooronRoot()
    nooron2 = NooronRoot()
    nooron1.system_basepath = '/home/smurp/src/nooron'
    print nooron1.system_basepath
    print nooron2.system_basepath
    print nooron1,nooron2
    #print nooron3['arf']
