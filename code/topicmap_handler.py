
__version__='$Revision: 1.14 $'[11:-2]
__cvs_id__ ='$Id: topicmap_handler.py,v 1.14 2002/08/23 03:39:15 smurp Exp $'

import string

# GooseWorks support
import GW
from GWApp import GWApp

import NooronRoot
import NooronApp

DEBUG = 0

from medusa import counter
import medusa
from medusa.default_handler import unquote

class ProcHandler:
    def __init__(self,graph):
        self.graph = graph
        self.source_uris = []
        
    def preMergeMap(self,refUri,addedThemes):
        if DEBUG: print "now merging in %s" % refUri
        print "now merging in %s" % refUri
        self.source_uris.append(refUri)
        
    def postMergeMap(self,e,refUri,addedThemes):
        if(e):
            print GW.errorString()
            GW.clearError()

    def unprocessedTopicRefUri(self,uris):
        if DEBUG: print "\nunprocessed topic ref uris"
        for u in uris:
            print u

    def unprocessedUris(self,uris):
        if DEBUG:
            print "\nunprocessed uris"
            for u in uris:
                print u

    def subjectEquivalence(self,sirs,scr):
        #print "subjectEquivalence:",sirs,scr
        self.graph.subjectEquivalence(sirs,scr);

    def association(self,a):
        self.graph.addAssociation(a)

    def startRootElement(doh):
        pass
        print "startRootElement:",doh.graph


    def endRootElement(doh):
        pass
        #if DEBUG: print "ending root element %s" % str(doh)


class GraphHandler:
    def association(assoc,role,member):
        if DEBUG: print "association: (%s,%s,%s)" % (str(assoc),
                                                     str(role),
                                                     str(member))
    def startRootElement():
        pass
        #if DEBUG: print "starting root element"
    def endRootElement():
        pass
        #if DEBUG: print "ending root element"



# A Medusa Handler

class topicmap_handler:

    def __init__(self,from_root,initial={}):
        self.hits = counter.counter()
        self.exceptions = counter.counter()
        self.from_root = from_root
        if type(initial) == type(''):
            self.graphs = {}
            self.load_map('initial_maps',initial)            
            self.load_graphs_from_initial(initial)
            print "graphs =",self.graphs
        else:
            self.graphs = initial
        self.initial = initial

    def load_graphs_from_initial(self,initial):
        #self.load_map('initial_maps',initial)
        app = self.graphs['initial_maps']
        resp = app.getAllClasses()
        print "resp =",resp
        tms = resp[0].getInstances()
        for tm in tms:
            bn = tm.getBaseNames()
            occs = tm.getOccurrences()
            if bn and occs:
                try:
                    uris = occs[0][2].getSCR().getUris()
                    spec = occs[0][2].getSCR().getData() or \
                           uris and str(uris[0]) or ''
                           

                    print "the spec is:",spec
                    print "SCR=",occs[0][2].getSCR().getData()
                    print
                    if DEBUG: print bn[0], spec
                    self.graphs[bn[0]] = spec
                except:
                    raise "","couldn't get uri for %s" % bn[0]

    def status(self):
        return medusa.producers.simple_producer("topicmap_handler maps:" +\
                                                str(self.graphs))

    def match(self,request):
        [path, params, query, fragment] = request.split_uri()

        retval = path.find(self.from_root)
        if retval < 0:
            retval = 0
        if DEBUG: print "topicmap_handler %s %s\n" % (path,str(retval))
        return retval


    def add_app(self,tm_name,gwapp):
        self.graphs[tm_name] = gwapp

    def parse_map(self,spec,tm_uri):
        u = GW.Uri(tm_uri)
        p = GW.Proc()
        g = GW.Graph(spec)
        ph = ProcHandler(g)
        p.setHandler(ph)
        g.startTransaction(GW.XRW)
        p.process(u)
        g.commitTransaction()
        return (g,ph.source_uris)

    def load_map(self,tm_name,tm_uri):
        if DEBUG: print tm_name,tm_uri
        
        if tm_uri[:5] == 'type=':
            spec = tm_uri
        else:
            spec = "type=Mem,name=%s" % tm_name

        spec_type = spec.split(',')[0].split('=')[1]
        print "spec = ",spec, spec_type

        if spec_type == "Mem":
            g,src_uris = self.parse_map(spec,tm_uri)
        else:
            src_uris = []
            g = GW.Graph(spec)
            
        #app = GWApp(g)
        app = NooronApp.NooronApp(g)
        app.set_src_uris(src_uris)
        if spec_type == 'Mem':
            app.use_indices_in_links = 1
            app.tm_uri = tm_uri
        else:
            app.use_indices_in_links = 0
            
        self.add_app(tm_name,app)
        
    def objectValues(self):
        graph_name = self.graphs.keys()
        retarr = []
        for n in graph_name:
            retarr.append(n)
        return retarr

    def get_map(self,tm_name):
        app = self.graphs[tm_name]
        if type(app) == type(''):
            self.load_map(tm_name,app)
        return self.graphs[tm_name]


    def handle_request(self,request):
        [path, params, query, fragment] = request.split_uri()
        # path extensions query
        while path and path[0] == '/':
            path = path[1:]

        if '%' in path or '+' in path:
            path = string.replace(path,'+',' ')
            path = unquote (path)
            print path

        obj = None
        app = None

        path_list = path.split('/')
        if len(path_list) < 3 and path[-1] != '/':
            loc = '/%s/' % (
                path
                )
            request['Location'] = loc
            print "FIXME: is it legal to forward to root-relative url?"
            request.error (301) # moved permanently
            return

        if path_list[-1] == '':
            del path_list[-1]

        if len(path_list) == 1:
            obj = self

        if len(path_list) > 1:
            tm_name = path_list[1]
            if self.graphs.has_key(tm_name):
                app = self.get_map(tm_name)
            else:
                request.error(401) # not found
                return

        if len(path_list) > 2:
            topic_name = path_list[2]
            topic_name = topic_name.replace('+',' ')
            if len(topic_name) > 5 and topic_name[:6] == 'index=':
                index = int(topic_name[6:])
                if DEBUG: print "fetching index ", index
                obj = app.TMObject(index)
            else:
                if DEBUG: print "topic_name =",topic_name
                nameIs = app.getAllWhereBaseNameIs(topic_name)
                nameContains = app.getAllWhereBaseNameContains(topic_name)
                if DEBUG:
                    print "nameIs ",len(nameIs),\
                          " nameContains ",len(nameContains)
                obj = nameIs and nameIs[0] or \
                      nameContains and nameContains[0] or \
                      app.getTopicWithAnchor(topic_name)

        if 1:
            app.publish(request,obj)
        else:
            if not obj:
                obj = app
                NooronRoot.NooronRoot().publish(request,obj)
            else:
                app.publish(request,obj)
