
__version__='$Revision: 1.13 $'[11:-2]
__cvs_id__ ='$Id: transformers.py,v 1.13 2002/12/04 18:08:12 smurp Exp $'

DEBUG = 1

import NooronRoot

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
        self.done = 0
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

class external_command_producer(typed_producer):
    """Get the mimetype from knowledge, the command (or cached file)
    from content.  Maybe external_command_producers can detect if
    their predecessors are external_command_producers and use unix pipes
    in place of more to funnel data into themselves."""
    os_pipes = 1
    def __init__(self,command,request=None,mimetype=None,extension=None):
        producer.__init__(self,command,request)
        self.mimetype = mimetype
        self.extension = extension
    def more(self):
        if self.done:
            return ''
        else:
            def makeNonBlocking(fd):
                fl = fcntl.fcntl(fd, FCNTL.F_GETFL)
                try:
                    fcntl.fcntl(fd, FCNTL.F_SETFL, fl | FCNTL.O_NDELAY)
                except AttributeError:
                    fcntl.fcntl(fd, FCNTL.F_SETFL, fl | FCNTL.FNDELAY)

            self.done = 1
            proc = popen2.Popen3(command,1)
            proc.tochild.write(input)
            proc.tochild.flush()
            proc.tochild.close()
            outfile = proc.fromchild
            outfd    = outfile.fileno()
            errfile  = proc.childerr
            errfd    = errfile.fileno()
            makeNonBlocking(outfd)
            makeNonBlocking(errfd)
            outdata = errdata = ''
            outeof = erreof = 0
            # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52296
            
            # 5 seconds grace period
            max_time_to_live = float(self.timeout + 5)

            if int(self.timeout) == 0:
                # set a one minute maxTTL if no timeout requested
                max_time_to_live = 60 
            #print "max_time_to_live",max_time_to_live,"\n"
            start_time = time.time()
            while 1:
                ready = select.select([outfd,errfd],[],[],1)

                if outfd in ready[0]:
                    outchunk = outfile.read()
                    if outchunk == '': outeof = 1
                    outdata = outdata + outchunk
                if errfd in ready[0]:
                    errchunk = errfile.read()
                    if errchunk == '': erreof = 1
                    errdata = errdata + errchunk
                if outeof and erreof: break
                if max_time_to_live + start_time < time.time():
                    break
                time.sleep(0.1)

            exit_code = proc.poll()

            if exit_code == -1:
                pid = proc.pid
                os.kill(pid,signal.SIGKILL)
                print self.content,'killed_child',str(pid)
            elif exit_code > 0:
                print self.content,'exit_code',str(exit_code)

            return outdata

class cached_external_command_producer(external_command_producer,
                                       medusa.producers.file_producer):
    def __init__(self,command,request=None,mimetype=None,extension=None,
                 md5val=None,cacheloc=None):
        self.cachedfile = None
        if cacheloc != None and extension != None and md5val != None:
            filename = os.path.join(cacheloc,md5val+extension)
            self.cachedfile = filename
            command = command + ' | tee ' + filename
        external_command_producer.__init__(self,command,request,
                                           mimetype,extension)
        
    def more(self):
        if self.done:
            return ''
        elif os.isfile(cachedfile):
            pass
            

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
        if self.done:
            return ''
        else:
            self.done = 1
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
        tr = nooron_root.template_root()
        template=tr.obtain(self.template_name,
                           request=request,
                           obj=content)
        template.title = self.template_name
        self.set_template(template)

    def set_template(self,template):
        self.template = template

    def more(self):
        if self.done:
            return ''
        else:
            self.done = 1
            print type(self.template)
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

class kb_html_producer(templated_producer):
    domain = ['pyokbc.PyKb.PyKb']
    extensions = ['pykb']
    def_mime_type = ['text/html'] 
    template_name = "kb_as_html"   

class directory_html_producer(templated_producer):
    domain = ['DirectoryFacade.DirectoryFacade'
              ,'topicmap_handler.topicmap_handler']
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    template_name = "directory_as_html"

class site_front_html_producer(templated_producer):
    domain = ['NooronRoot.NooronRoot']
    extensions = ['html','htm']
    def_mime_type = ['text/html']
    template_name = "site_front_as_html"



class pipeline:
    def __init__(self,producers,request):
        self.producers = producers
        self.request = request

    def mime_type(self):
        try:
            return self.producers[-1].mime_type()
        except:
            return 'text/html'            

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


"""
IN                      OUT   TYPE     WHAT
=============================================
nooron_app              .dbk  garment  nooron_app_as_docbook
pattern_language_app    .dbk  garment  pattern_language_as_docbook, ...
pattern_language_app    .dot  garment  pattern_language_as_dot, ...
application/x-graphviz  .ps   command  dot -Tps
application/x-graphviz  .jpg  command  dot -Tjpeg
.dbk                    .ps   command  docbook2ps
.dbk                    .pdf  command  docbook2pdf
"""
