
__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: extension_handler.py,v 1.1 2002/07/18 20:44:37 smurp Exp $'


import inspect_module
import transformers
import string,re
import medusa

class extension_handler:
    """Detect the extension and apply an appropriate output producer."""

    def __init__(self):
        self.producers = {}
        for trans in inspect_module.classes_in_module(transformers):
            self.register(trans)

    def status(self):
        return medusa.producers.simple_producer("PipelineFactory extensions: "+str(self.producers))

    def register(self,producer):
        try:
            exts = producer.extensions
        except:
            print producer.__name__, "is not a concrete producer class"
            exts = []
        for ext in exts:
            self.producers[ext] = producer

    def mime_type(self,ext):
        if self.producers.has_key(ext):
            return self.producers[ext].mime_type
        else:
            return 'text/plain'

    def match(self,request):
        ### FIXME the real match test is, do we recognize the object and the extensions?
        return 1
        there_are_extensions_p = len(self.extension_list(request))
        return there_are_extensions_p

    def extension_list(self,request):
        [path, params, query, fragment] = request.split_uri()
        m = re.findall(r'\.(?P<exts>\w+)*',path)
        if m:
            return m
        else:
            return []

    def transformers_from_extensions(self,extensions,object):
        trans = []
        count = 0
        prev = None
        for ext in extensions:
            if self.producers.has_key(ext):
                if prev:
                    # pass the previous transformer to the next one
                    next = self.producers[ext](prev)
                    #print "queing transformer, transformer: ",next,prev
                    trans.append(next)
                else:
                    # pass the object to the first (and only the first) producer
                    next = self.producers[ext](object)
                    #print "queing transformer, string     : ",next, type(object)
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
