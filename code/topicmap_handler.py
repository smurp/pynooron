
__version__='$Revision: 1.9 $'[11:-2]
__cvs_id__ ='$Id: topicmap_handler.py,v 1.9 2002/08/02 23:44:41 smurp Exp $'


# GooseWorks support
import GW
from GWApp import GWApp

import NooronRoot

DEBUG = 1

from medusa import counter
import medusa


class ProcHandler:
    def __init__(self,graph):
        self.graph = graph
        
    def preMergeMap(self,refUri,addedThemes):
        if DEBUG: print "now merging in %s" % refUri      
        
    def postMergeMap(self,e,refUri,addedThemes):
        if(e):
            print GW.errorString()
            GW.clearError()

    def unprocessedTopicRefUri(self,uris):
        if DEBUG: print "\nunprocessed uris"
        for u in uris:
            print u

    def subjectEquivalence(self,sirs,scr):
        self.graph.subjectEquivalence(sirs,scr);

    def association(self,a):
        self.graph.addAssociation(a)

    def endRootElement(doh):
        if DEBUG: print "ending root element %s" % str(doh)


class GraphHandler:
    def association(assoc,role,member):
        if DEBUG: print "association: (%s,%s,%s)" % (str(assoc),
                                                     str(role),
                                                     str(member))
    def startRootElement():
        if DEBUG: print "starting root element"
    def endRootElement():
        if DEBUG: print "ending root element"



# A Medusa Handler

class topicmap_handler:

    def __init__(self,from_root,initial={}):
        self.hits = counter.counter()
        self.exceptions = counter.counter()
        self.from_root = from_root
        self.graphs = initial
        self.initial = initial

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


    def load_map(self,tm_name,tm_uri):
        if DEBUG: print tm_name,tm_uri
            
        u = GW.Uri(tm_uri)

        p = GW.Proc()

        if tm_uri[:5] == 'type=':
            spec = tm_uri
        else:
            spec = "type=Mem,name=%s" % tm_name
            
        g = GW.Graph(spec)

        ph = ProcHandler(g)

        p.setHandler(ph)
        #g.setHandler(gh)

        g.startTransaction(GW.XRW)
        p.process(u)
        g.commitTransaction()

        app = GWApp(g)
        app.tm_uri = tm_uri        
        self.add_app(tm_name,app)
        
        if DEBUG: print self.graphs[tm_name]


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

        if '%' in path:
            path = unquote (path)

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
            path = app.tm_uri
            topic_name = topic_name.replace('+',' ')
            if len(topic_name) > 5 and topic_name[:6] == 'index=':
                index = int(topic_name[6:])
                print "fetching index ", index
                obj = app.TMObject(index)
            else:
                print "fetching topic_name " + topic_name
                obj = app.getTopicWithID('%s#%s' % (path,topic_name))
            
        if not obj:
            obj = app

        NooronRoot.NooronRoot().publish(request,obj)
        
