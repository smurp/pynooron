
import string

import NooronRoot
from NooronPageTemplate import NooronPageTemplate



class TemplateManager:
    """Each nested template directory gets one of these acquisition supporters."""
    aq_parent = None
    def __init__(self,parent,path):
        self.aq_parent = parent
        self.path = path
    def setObject(self,id,obj):
        #obj.aq_inner = AqInner(self)
        obj.aq_parent = self
    def __str__(self):
        return "TemplateManager_"+str(self.__dict__)
        
    def obtain_template_src(self,template_name):
        #NooronRoot = NooronRoot.NooronRoot
        fname = NooronRoot.NooronRoot().make_fname([self.path,template_name])
        file = open(fname,'r')
        out = string.join(file.readlines(),"")
        file.close()
        return out

    def obtain(self,template_name,request=None,obj=None):
        template = NooronPageTemplate(request=request,
                                      obj=obj,
                                      container=self)
        self.setObject(template_name,template)
        src = self.obtain_template_src(template_name)
        template.write(src)
        return template
        
