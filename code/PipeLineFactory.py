
__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: PipeLineFactory.py,v 1.1 2002/07/22 19:33:43 smurp Exp $'


import inspect_module
import transformers
import string,re
import medusa

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

    def status(self):
        return medusa.producers.simple_producer("PipelineFactory extensions: "+str(self.transformers))

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

    def transformers_from_extensions(self,extensions,object):
        try:
            klass = object.__class__
        except:
            klass = None
        domain = str(klass)
        trans = []
        count = 0
        prev = None
        for ext in extensions:
            if self.transformers.has_key(ext):
                if prev:
                    # pass the previous transformer to the next one
                    next = self.transformers[ext][0](prev)
                    #print "queing transformer, transformer: ",next,prev
                    trans.append(next)
                else:
                    # treat the first producer differently
                    if klass:
                        producer = self.transformer_for_domain(ext,domain)
                        if producer:
                            # if there is a special one for obj.__class__, use it
                            next = producer(object)
                        else:
                            # just use the default one based on the extension
                            next = self.transformers[ext][0](object)
                    trans.append(next)
                    prev = next
            else:
                raise 'ExtensionError',"There is no transformer or generator for %s" % ext
        #print "\n" 
        return [next]

    def resolve_object(self,request):
        return "This is the default text, and the path was: %s" % request.split_uri()[0]

        
    def build_pipeline(self,request,object=None):
        if not object:
            object = self.resolve_object(request)
        extens = self.extension_list(request)
        if not extens:
            extens.append('html')
            ### FIXME we should really as the object and the user about defaults and preferences
        transs = self.transformers_from_extensions(extens,object)
        return transformers.pipeline(transs,request)

    def handle_request(self,request):
        pipeline = self.build_pipeline(request)
        pipeline.publish()
