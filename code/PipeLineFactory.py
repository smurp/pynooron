
__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: PipeLineFactory.py,v 1.2 2002/07/29 22:37:50 smurp Exp $'

DEBUG = 0

import inspect_module
import transformers
import string,re
import medusa
from NooronRoot import NooronRoot

class PipeLineFactory:
    """Detect the extension and apply an appropriate output producer."""

    def __init__(self):
        self.transformers = {}
        for trans in inspect_module.classes_in_module(transformers):
            self.register(trans)

    def transformer_for_domain(self,ext,domain):
        for trans in self.transformers[ext]:
            if domain in trans.domain:
                return trans
        return None

    def transformer_from_uri(self,object,request,uri):
        """Return a transformer with a template given by uri."""
        if uri:
            if uri[0:7] == 'http://':
                raise "NotYetImplemented","loading of arbitrary templates by uri"
            if uri[0] == '/':
                raise "NotYetImplemented","loading of templates by full path"
            if uri[0] == '..':
                raise "NotYetImplemented","loading of templates by relative path"
            return transformers.arbitrary_producer(object,request,uri)
        else:
            return None
        
        
    def status(self):
        return medusa.producers.simple_producer("PipelineFactory extensions: " + \
                                                str(self.transformers))

    def register(self,producer):
        try:
            exts = producer.extensions
        except:
            #print producer.__name__, "is not a concrete producer class"
            exts = []
        for ext in exts:
            if not self.transformers.has_key(ext):
                self.transformers[ext] = []
            self.transformers[ext].append(producer)

    def mime_type(self,ext):
        if self.transformers.has_key(ext):
            return self.transformers[ext][0].mime_type
        else:
            return 'text/plain'

    def extension_list(self,request):
        [path, params, query, fragment] = request.split_uri()
        m = re.findall(r'\.(?P<exts>\w+)*',path)
        if m:
            return m
        else:
            return []

    def transformers_from_extensions(self,extensions,object,request):
        #[path,params,query,fragment] = request.split_uri()
        query = request.split_query()
        try:
            klass = object.__class__
        except:
            klass = str(type(object))
        domain = str(klass)
        if DEBUG: print "klass = ", klass
        trans = []
        count = 0
        prev = None
        next = None
        if DEBUG: print "extensions: ", str(extensions)
        for ext in extensions:
            if DEBUG: print "ext = ", ext
            if self.transformers.has_key(ext):
                if prev:
                    # pass the previous transformer to the next one
                    next = self.transformers[ext][0](prev)
                    if DEBUG: print "nth: ",next
                    trans.append(next)
                else:
                    # treat the first producer differently
                    if DEBUG: print "query =",query
                    
                    if query.get('with_template'):
                        producer = transformers.arbitrary_producer

                    elif klass:
                        producer = self.transformer_for_domain(ext,domain)
                    if producer:
                        # if there is a special one for obj.__class__, use it
                        next = producer(object,request)
                    else:
                        # just use the default one based on the extension
                        if isinstance(object,transformers.typed_producer):
                            next = object
                        else: 
                            if DEBUG: print "using default producer based on extension for " + str(object)
                            next = self.transformers[ext][0](object,request)
                    if DEBUG: print "1st: ",next
                    trans.append(next)
                    prev = next
            else:
                #raise 'ExtensionError',"There is no transformer or generator for %s" % ext
                if DEBUG: print "There is no transformer or generator for %s" % ext
        if not extensions or not next:
            if DEBUG: print "next = object"
            trans.append(object)
            next = object
        #print "\n"
        if DEBUG: print "next = ",next
        return [next]

    def resolve_object(self,request):
        return "This is the default text, and the path was: %s" % request.split_uri()[0]

        
    def build_pipeline(self,request,object=None):    #print "the object is ",object
        if not object:
            object = self.resolve_object(request)
        extens = self.extension_list(request)
        if not extens:
            extens.append('html')
            ### FIXME we should really as the object and the user about
            ###       defaults and preferences
        transs = self.transformers_from_extensions(extens,object,request)
        return transformers.pipeline(transs,request)

    def handle_request(self,request):
        pipeline = self.build_pipeline(request)
        pipeline.publish()
