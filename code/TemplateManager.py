
__version__='$Revision: 1.6 $'[11:-2]
__cvs_id__ ='$Id: TemplateManager.py,v 1.6 2002/10/16 19:29:49 smurp Exp $'

DEBUG = 0

import string

import NooronRoot
from NooronPageTemplate import NooronPageTemplate

import urlparse
import urllib

class TemplateManager:

    aq_parent = None
    latest = {}
    def __init__(self,parent,path):
        self.aq_parent = parent
        self.path = path
    def setObject(self,id,obj):
        #obj.aq_inner = AqInner(self)
        obj.aq_parent = self

    def __getitem__(self,key):
        return self.obtain(key,
                           self.latest.get('request'),
                           self.latest.get('obj'))
        
    def __str__(self):
        return "TemplateManager_"+str(self.__dict__)
        
    def obtain_template_src(self,template_name):
        #NooronRoot = NooronRoot.NooronRoot
        template_uri = template_name

        #url_tup = urlparse.urlparse(template_name,'file')
        if template_name.find('http:') == 0 or \
           template_name.find('https:') == 0 or \
           template_name.find('ftp:') == 0:
            if DEBUG: print "start retrieving",template_uri
            (fname,headers) = urllib.urlretrieve(template_uri)
            if DEBUG: print "end   retrieving"
        else:
            if template_name.find('file:') == 0:
                template_name = template_name[7:]
            fname = nooron_root.make_fname([self.path,
                                                        template_name])
        file = open(fname,'r')
        out = string.join(file.readlines(),"")
        file.close()
        return out

    def obtain(self,template_name,request=None,obj=None):
        #print "obtaining obj=",obj,"request =",request,"template_name = ",template_name
        if request and obj:
            self.latest.update({'request':request,
                                'obj':obj})
        #print "TemplateManger.obtain() obj =",obj,"self =",self
        template = NooronPageTemplate(request=request,
                                      obj=obj,
                                      container=self)
        print "template_name =",template_name
        self.setObject(template_name,template)
                
        src = self.obtain_template_src(template_name)

        template.write(src)
        return template
        
    
