
__version__='$Revision: 1.8 $'[11:-2]
__cvs_id__ ='$Id: transformers.py,v 1.8 2002/08/07 20:23:41 smurp Exp $'

DEBUG = 0

#from NooronRoot import NooronRoot
import NooronRoot
#NooronRoot = NooronRoot.NooronRoot

from NooronPageTemplate import NooronPageTemplate
import types
import string
import medusa

class producer:
    def more_content(self):
        try:
            return self.content.more()
        except:
            return str(self.content)
    
    def __init__(self,content,request=None):
        self.content = content
        self.written = 0
        self.request = request

class typed_producer(producer):
    domain = []
    range = 'cdata'
    def mime_type(self):
        if self.def_mime_type:
            return self.def_mime_type[0]
        else:
            try:
                return self.content.mime_type()
            except:
                return 'text/plain'
    

class typed_file_producer(typed_producer,medusa.producers.file_producer):
    def_mime_type = ['text/plain']
    def __init__(self,content,request=None):
        producer.__init__(self,content,request)
        medusa.producers.file_producer.__init__(self,content)


class transformer(producer):
    """A transformer is a producer which processes a stream of character data.

    They can be nested arbitrarily.  Examples include upper, lower, gz.
    """
    domain = []     # how to use this stuff?
    range = 'text/plain'  # oh, how to use it!
    def more(self):
        return self.more_content()

class txt(producer):
    extensions = ['txt']
    def_mime_type = ['text/plain']
    def more(self):
        if self.written:
            return ''
        else:
            self.written = 1
            return str(self.more_content())

class tar(transformer):
    extensions = ['tar']
    def_mime_type = ['application/x-tar']

class gz(transformer):
    extensions = ['gz']
    def_mime_type = ['application/x-gzip']
    # http://www.iol.ie/~alank/python/httpcomp.html#modpython

class upper(transformer):
    extensions = ['AZ']
    def_mime_type = None
    def more(self):
        return string.upper(self.more_content())

class lower(transformer):
    extensions = ['az']
    def_mime_type = None
    def more(self):
        return string.lower(self.more_content())

class tgz(transformer):
    extensions = ['tgz']    
    def_mime_type = ['application/x-gzip']    

class templated_producer(typed_producer):
    """Producers which generate their data through a PageTemplate."""
    template_name = "primordial"
    def __init__(self,content,request=None):
        #print "templated_producer obj=",content,"request =",request
        producer.__init__(self,content)
        tr = NooronRoot.NooronRoot().template_root()
        template=tr.obtain(self.template_name,
                           request=request,
                           obj=content)
        template.title = self.template_name
        self.set_template(template)

    def set_template(self,template):
        self.template = template

    def more(self):
        if self.written:
            return ''
        else:
            self.written = 1
            #print type(self.template)
            return self.template(content=str(self.more_content()))

class arbitrary_producer(templated_producer):
    domain = []
    extensions = []
    def_mime_type = ['text/html']
    template_name = ''
    def __init__(self,content,request=None,uri=None):
        effquery = request.effective_query()
        self.template_name = effquery.get('with_template')
        templated_producer.__init__(self,content,request)
        

class topic_html_producer(templated_producer):
    """Render a topic in a fashion specific to its class, or else generically.

    It does this by attemping to find a template called
      'instance_of_CLASSNAME_as_html'
    or should it be
      NR/templates/by_tclass/TKLASS/instance_as_html
      NR/templates/by_tclass/TKLASS/instance_as_svg
      NR/templates/by_tclass/TKLASS/instance_as_html?cvstag=TRICKY
    and uses it or else it just uses 'topic_as_html'."""
    domain = ['GWApp.TMObject']
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    template_name = "topic_as_html"

class tclass_html_producer(templated_producer):
    """Render a generic class in a generic fashion.

    Currently unused since no technique has been devised for gracefully
    employing this template depending on whether the topic is a class.
    """
    domain = ['GWApp.TMObject']
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    template_name = "tclass_generic_as_html"

class topicmap_html_producer(templated_producer):
    """Render a topicmap itself."""
    domain = ['NooronApp.NooronApp'
              ,'GWApp.GWApp' # deprecated
              ]
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    template_name = "topicmap_as_html"

class directory_html_producer(templated_producer):
    domain = ['DirectoryFacade.DirectoryFacade'
              ,'NooronRoot.NooronRoot'
              ,'topicmap_handler.topicmap_handler']
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    template_name = "directory_as_html"

    

#class python_html_producer(typed_file_producer):
#    domain = ["<type 'file'>"]
#    extensions = ['py']
#    def_mime_type = ['text/plain']


class pipeline:
    def mime_type(self):
        try:
            return self.producers[-1].mime_type()
        except:
            return 'text/html'            

    def __init__(self,producers,request):
        self.producers = producers
        self.request = request
    def show_pipes(self):
        retval = "pipes = "
        for x in self.producers:
            if isinstance(x,types.ClassType):
                retval = retval + x.__class__.__name__
            else:
                retval = retval + str(x)
        return retval + "\n\n" 
    def more (self):
        while len(self.producers):
            p = self.producers.pop(0)
            d = p.more()
            if DEBUG:
                print """==================\n%s %s %s\n==================\n""" % \
                      (str(len(d)),
                       str(len(self.producers)),
                       p.__class__.__name__)
            if d:
                return d
            else:
                self.producers.pop()
        else:
            return ''

    def publish(self):
        request = self.request
        request['Content-Type'] = self.mime_type()
        response = []
        cont = 1
        while cont:
            ut = self.more()
            response.append(ut)
            cont = len(ut)
        resp = string.join(response,"")
        request['Content-Length'] = len(resp)

        blocksize = 1024
        leng = len(resp)
        more = leng
        s = 0
        e = blocksize
        while more:
            request.push(resp[s:e])
            s = s + blocksize
            e = e + blocksize
            more = s < leng
        request.done()

