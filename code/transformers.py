
# PageTemplate Support
import sys
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python')
sys.path.append('/usr/local/zope/Zope-2.5.1/lib/python/Products')
from PageTemplates.PageTemplate import PageTemplate


import types
import string
import medusa

topic_template = """
<html><head><title>Boo</title></head><body>
<div>
  <pre tal:define="breadcrumbs options/breadcrumbs" tal:replace="python:breadcrumbs">???</pre>
</div>
        <hr>
        <dl>
          <dt>path<dd>%s
          <dt>params<dd>%s
          <dt>query<dd>%s
          <dt>fragment<dd>%s
        </dl>
        <hr>
        timstamp = %s
        </body></html>
"""

class producer:
    domain = None
    range = 'cdata'
    def mime_type(self):
        if self.def_mime_type:
            return self.def_mime_type[0]
        else:
            try:
                return self.content.mime_type()
            except:
                return 'text/plain'

    def more_content(self):
        try:
            return self.content.more()
        except:
            return str(self.content)
    
    def __init__(self,content):
        self.content = content
        self.written = 0

class transformer(producer):
    domain = 'cdata'
    range = None
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

class topicmap_html_producer(producer):
    domain = ['topicmap']
    extensions = ['html','htm']
    def_mime_type = ['text/html']

class topic_html_producer(producer):
    domain = ['topic']
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    def __init__(self,content,template=None):
        producer.__init__(self,content)
        if not template:
            template=PageTemplate()
            template.write(topic_template)

#            template.write("""Not yellow here.<table bgcolor="yellow" border="1"><tr><td>
#            <pre tal:define="x options/x" tal:replace="python:x">???</pre></td></tr></table>
#            Not yellow here.""")

            self.set_template(template)

    def set_template(self,template):
        self.template = template

    def more(self):
        if self.written:
            return ''
        else:
            self.written = 1
            return self.template(breadcrumbs=str(self.more_content()))

class pipeline:
    def mime_type(self):
        return self.producers[-1].mime_type()
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
            #print p.__class__.__name__,len(self.producers),d
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
        resp = string.join(response,"\n")
        request['Content-Length'] = len(resp)        
        request.push(resp)
        request.done()
