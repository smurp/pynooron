
__version__='$Revision: 1.10 $'[11:-2]
__cvs_id__ ='$Id: TemplateManager.py,v 1.10 2003/04/22 06:53:24 smurp Exp $'

DEBUG = 0

SAFETY = 1

if SAFETY:
    print "Notice: TemplateManager.SAFETY is ON"
else:
    print """
Warning: TemplateManager.SAFETY is OFF
         This means that if the query string contains
           ?with_template=http://some.random.url/garmie.html
           ?with_template=file:///some/secret/on/your/drive
           ?with_template=file:///etc/passwd
         Then the contents of that url will be obtained
         and executed as a NooronPageTemplate.  This is
         currently hideously dangerous for three reasons:
           1) if NooronPageTemplate SAFETY is OFF
              then python in templates is unrestricted and
              has all the power of the user running the Nooron.
           2) there is currently nothing to prevent template authors
              from inserting (or modifying) instances of
                /know/transformers_ontology/ExternalCommand
              which when run have all the power of the unix user.
           3) there are probably other holes in the restriction of
              python in templates, specifically through the
              manipulation of objects accessible to templates.
         It is safe to run a Nooron instance when
              TemplateManager SAFETY is OFF
         if the Nooron instance is behind a firewall on a
         single user machine or on a completely trusted LAN.
              """

import string
import os
import NooronRoot
from NooronPageTemplate import NooronPageTemplate

import urlparse
import urllib

def _make_allowed_fname(allowed_place,kb_locator):
    #if DEBUG: print "make_fname",frag
    #print "_make_allowed_fname",allowed_place,kb_locator
    fullpath = os.path.join(allowed_place,kb_locator)
    normpath = os.path.normpath(fullpath)
    #if DEBUG: print "normpath =",normpath
    if normpath.find(allowed_place) != 0:
        raise "Illegal path requested",\
              "%s not in %s" % (normpath,allowed_place)
    return normpath


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
        
    def obtain_template_src_and_stats(self,template_name):
        #NooronRoot = NooronRoot.NooronRoot
        template_uri = template_name


        #url_tup = urlparse.urlparse(template_name,'file')
        for a_place in self.path:
            if SAFETY:
                fname = _make_allowed_fname(a_place, template_name)
            else:
                if template_name.find('http:') == 0 or \
                       template_name.find('https:') == 0 or \
                       template_name.find('ftp:') == 0:
                    if DEBUG: print "start retrieving",template_uri
                    (fname,headers) = urllib.urlretrieve(template_uri)
                    if DEBUG: print "end   retrieving"
                else:
                    if template_name.find('file://') == 0:
                        template_name = template_name[7:]
                        fname = _make_allowed_fname(a_place, template_name)
            try:
                file = open(fname,'r')
                out = string.join(file.readlines(),"")
                file.close()
                break
            except:
                continue
        
        st = os.stat(fname)
        stats = {'UID':st[4],
                 'GID':st[5],
                 'SIZE':st[6],
                 'ATIME':st[7],
                 'MTIME':st[8],
                 'CTIME':st[9]}
        return (out,stats)

    def obtain(self,template_name,request=None,obj=None):
        #print "obtaining obj=",obj,"request =",request,"template_name = ",template_name
        if request and obj:
            self.latest.update({'request':request,
                                'obj':obj})
        #print "TemplateManger.obtain() obj =",obj,"self =",self
        template = NooronPageTemplate(request=request,
                                      obj=obj,
                                      container=self)
        #print "template_name =",template_name
        self.setObject(template_name,template)
                
        (src,stats) = self.obtain_template_src_and_stats(template_name)

        template.write(src)
        template._stats = stats
        
        return template
        
    
