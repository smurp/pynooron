
__version__='$Revision: 1.4 $'[11:-2]
__cvs_id__ ='$Id: topicmap_handler.py,v 1.4 2002/07/24 11:02:41 smurp Exp $'


# GooseWorks support
import GW
from GWApp import GWApp

DEBUG = 1
from medusa import counter
import medusa

def link_to_tmobject(topic):
    return """<a href="../TMObject/%s">%s</a>""" % ( topic.getIndex(),
                                                        str(topic.getBaseNames()) )

class ProcHandler:
    def __init__(self,graph):
        self.graph = graph
        
    def preMergeMap(self,refUri,addedThemes):
        print "now merging in %s" % refUri      
        
    def postMergeMap(self,e,refUri,addedThemes):
        if(e):
            print GW.errorString()
            GW.clearError()

    def unprocessedTopicRefUri(self,uris):
        print "\nunprocessed uris"
        for u in uris:
            print u

    def subjectEquivalence(self,sirs,scr):
        self.graph.subjectEquivalence(sirs,scr);

    def association(self,a):
        self.graph.addAssociation(a)

    def endRootElement(doh):
        print "ending root element %s" % str(doh)


class GraphHandler:
    def association(assoc,role,member):
        print "association: (%s,%s,%s)" % (str(assoc),str(role),str(member))
    def startRootElement():
        print "starting root element"
    def endRootElement():
        print "ending root element"



# A Medusa Handler

class topicmap_handler:

    #  see canned_queries.py for old stuff

    def __init__(self,from_root,pipeline_factory):
        self.hits = counter.counter()
        self.exceptions = counter.counter()
        self.from_root = from_root
        self.graphs = {}
        self.pipeline_factory = pipeline_factory


    def status(self):
        return medusa.producers.simple_producer("topicmap_handler maps:" + str(self.graphs))


    def match(self,request):
        [path, params, query, fragment] = request.split_uri()
        retval = path.find(self.from_root)
        if retval < 0:
            retval = 0
        return retval


    #tmh.add_graph('jill',"type=MySQL,name=jill,user=smurp,pass=trivialpw")
    def add_graph(self,tm_name,spec): # deprecated, see import_topicmap
        g = GW.Graph(spec)
        self.graphs[tm_name] = GWApp(g)

    def import_topicmap(self,tm_name,tm_uri):
        if DEBUG:
            print tm_name,tm_uri
            
        u = GW.Uri(tm_uri)

        p = GW.Proc()

        g = GW.Graph("type=Mem,name=%s" % tm_name)

        ph = ProcHandler(g)
        #gh = GraphHandler()

        p.setHandler(ph)
        #g.setHandler(gh)

        g.startTransaction(GW.XRW)
        p.process(u)
        g.commitTransaction()

        app = GWApp(g)
        self.graphs[tm_name] = app
        app.tm_uri = tm_uri
        
        if DEBUG:
            print self.graphs[tm_name]

    def available_graphs(self):
        graph_name = self.graphs.keys()
        retval = "<h3>available graphs</h3>"
        for n in graph_name:
            retval = retval + """<a href="%s/">%s</a><br>\n""" % (n,n)
        return retval


    def available_queries_for_graph(self,tm_name):
        #query_names = self.canned_queries.keys() + self.graphs[tm_name].__class__.__dict__.keys()
        query_names = self.graphs[tm_name].__class__.__dict__.keys()        
        retval = "<h3>available queries</h3>"
        for n in query_names:
            retval = retval + """<a href="%s">%s</a><br>\n""" % (n,n)
        return retval

    def breadcrumbs(self,path_list):
        path = "/"
        retval = "\n<!-- breadcrumbs() start -->\n"
        for i in path_list:
            retval = retval + " / "
            path = path + i + "/"
            retval = retval + """<a href="%s">%s</a>\n""" % (str(path),str(i))

        retval = retval + "<!-- breadcrumbs() end -->\n"
        return retval

    def graph_query(self,tm_name,qname):
        app = self.graphs[tm_name]
        if not hasattr(app,qname):
            return "Can not find " + qname
        retval = ""
        for t in apply(getattr(app,qname),[],{}):
            basenames = t.getBaseNames()
            if len(basenames):
                label = basenames[0]
                link = "topic/" + label
            else:
                label =  "index=%s" % str(t.getIndex())
                link = "TMObject/%s" % t.getIndex()
            retval = retval + """<LI><a href="%s">%s</a>""" % (link,label)
        return retval


    def present_tmobject(self,topic):
        retval =  "a TMObject<br>"

        sir_summ = ""
        for sir in topic.getSIRs():
            sir_summ = """<a href="%s">%s</a><br />""" % \
                       ( sir.getUris()[0],sir.getUris()[0] )
        if sir_summ:
            sir_summ = "<b>subject indicators</b><br>" + sir_summ + "\n"

        inst_summ = ""
        for inst in topic.getInstances():
            inst_summ = link_to_tmobject(inst)
        if inst_summ:
            inst_summ = "<b>direct instances</b><br>" + inst_summ + "\n"

        occ_summ = ""
        for occ in topic.getOccurrences():
            occ_summ = occ_summ + \
                       "\n<LI>" + link_to_tmobject(occ[0]) + \
                       " -- "   + link_to_tmobject(occ[0]) + \
                       " -- "   + link_to_tmobject(occ[0]) 
                       
        if occ_summ:
            occ_summ = "<b>occurences</b><br>\n" + occ_summ + "\n"

        bn_summ = ""
        for bn in topic.getBaseNames():
            bn_summ = bn_summ + """<LI>%s""" % bn
        if bn_summ:
            bn_summ = "<b>base names</b><br>\n" + bn_summ + "<br>\n"
            
        return retval + sir_summ + bn_summ + inst_summ + occ_summ


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
        header = self.breadcrumbs(path_list) + "<hr>\n"        
        if path_list[-1] == '':
            del path_list[-1]

        if len(path_list) > 1:
            tm_name = path_list[1]
            app = self.graphs[tm_name]

        if len(path_list) > 2:
            topic_name = path_list[2]
            path = app.tm_uri
            obj = app.getTopicWithID('%s#%s' % (path,topic_name))
            
            
        if not obj:
            obj = app
        pl = self.pipeline_factory.build_pipeline(request,obj)
        pl.publish()
        
