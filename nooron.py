#!/usr/bin/python2

__version__='$Revision: 1.2 $'[11:-2]
__cvs_id__ ='$Id: nooron.py,v 1.2 2002/07/11 17:17:39 smurp Exp $'

import string
import GW,sys,os

from GWApp import GWApp

import asyncore
from medusa import http_server
from medusa import default_handler
from medusa import logger
from medusa import script_handler
from medusa import filesys
from medusa import status_handler

from medusa import counter


"""
Nooron -- a whack at a proof of concept for the collective intelligence
approach described at http://www.noosphere.org/

"""


DEBUG = 1

PUBLISHING_ROOT='/home/smurp/src/nooron'

class sample_input_collector:
    def __init__ (self, request, length):
        self.request = request
        self.length = length

    def collect_incoming_data (self, data):
        print 'data from %s: <%s>' % (self.request, repr(data))

class post_script_handler (script_handler.script_handler):

    def handle_request (self, request):
        if request.command == 'post':
            ic = sample_input_collector (request)
            request.collector = ic
            print request.header

        return script_handler.script_handler.handle_request (self, request)


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



#   Utility Functions

def link_to_tmobject(topic):
    return """<a href="../TMObject/%s">%s</a>""" % ( topic.getIndex(),
                                                         str(topic.getBaseNames()) )



# A Medusa Handler

class topicmap_handler:

    canned_queries = {
       
        'basenames':
        """
 FROM {'http://www.topicmaps.org/xtm/1.0/psi1.xtm#at-topic-basename'}
 DO
   TRAVERSE xAXa
   TRAVERSE aAMm({'http://www.topicmaps.org/xtm/1.0/psi1.xtm#role-basename'})
 DONE
    """,

        'occurrences':
        """
 FROM {'http://www.topicmaps.org/xtm/1.0/psi1.xtm#at-topic-occurrence'}
 DO
   TRAVERSE xAXa
   TRAVERSE aAMm({'http://www.topicmaps.org/xtm/1.0/psi1.xtm#role-occurrence'})
 DONE
        """,


        'classes':
        """
 FROM {'http://www.topicmaps.org/xtm/1.0/psi1.xtm#at-class-instance'}
 DO
   TRAVERSE xAXa
   TRAVERSE aAMm({'http://www.topicmaps.org/xtm/1.0/psi1.xtm#role-class'})
 DONE
        """,


        'instances':
        """
 BASE 'http://www.topicmaps.org/xtm/1.0/psi1.xtm'
 FROM {'#at-class-instance'}
 DO
   TRAVERSE xAXa
   TRAVERSE aAMm({'#role-instance'})
 DONE""",


        'players':
        """
        BASE 'http://www.topicmaps.org/xtm/1.0/psi1.xtm'        
        FROM {'#role-role'} DO TRAVERSE rAMm({'#role-role'})
                   TRAVERSE mAMa({'#role-topic'}) 
                   TRAVERSE aAMm({'#role-basename'})
                   DONE
        """,


        'templates':
        """
 BASE 'http://www.topicmaps.org/xtm/1.0/psi1.xtm'
 FROM
     FROM ALL
     DO
       TRAVERSE aAXx
     DONE
 DO
   TRAVERSE mAMa({'#role-topic'})
   TRAVERSE aAMm({'#role-basename'})
 DONE
        """,

        'subclasses':
        """
        FROM {'%s'} DO TRAVERSE mAMa({'#role-superclass'})
        TRAVERSE aAMm({'#role-subclass'})
        TRAVERSE mAMa({'#role-topic'}) 
        TRAVERSE aAMm({'#role-basename'})
        DONE AS STRINGS
        """
        
        }

    def perform_canned_query(self,graph,query_name,as=None,frum=None,show_query=None):
        # http://www.etopicality.com/presentations/NY_2001/slide19.html

        query = self.canned_queries[query_name]

        retval = []
        if show_query:
            retval.append("<pre>%s</pre>" % query)
        if as:
            query = query + " as " + as
        if frum:
            query = query % frum
        for i in graph.STMQLExec(query):
            retval.append(str(i))
        return string.join(retval,"<br>\n")

    def __init__(self,tm_uri):
        #self.tm_uri = tm_uri
        self.hits = counter.counter()
        self.exceptions = counter.counter()
        self.from_root = 'map'
        self.graphs = {}

    def match(self,request):
        [path, params, query, fragment] = request.split_uri()
        retval = path.find(self.from_root)
        if retval < 0:
            retval = 0
        return retval

    def add_graph(self,tm_name,spec):
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

        
        self.graphs[tm_name] = GWApp(g)
        if DEBUG:
            print self.graphs[tm_name]

    def available_graphs(self):
        graph_name = self.graphs.keys()
        retval = "<h3>available graphs</h3>"
        for n in graph_name:
            retval = retval + """<a href="%s/">%s</a><br>\n""" % (n,n)
        return retval

    def is_query(self,query_name):
        return self.canned_queries.has_key(query_name)

    def available_queries_for_graph(self,tm_name):
        query_names = self.canned_queries.keys() + self.graphs[tm_name].__class__.__dict__.keys()
        retval = "<h3>available queries</h3>"
        for n in query_names:
            retval = retval + """<a href="%s">%s</a><br>\n""" % (n,n)
        return retval

    def do_query(self,tm_name=None,query_name='instances',as=None):
        if not self.graphs.has_key(tm_name):
            return "map '%s' not known" % tm_name
        g = self.graphs[tm_name].graph
        #g.startTransaction(GW.XRO)
        try:
            response = self.perform_canned_query(g,query_name,as=as)
        except:
            pass
        #g.commitTransaction()
        return response

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

    def topic(self,app,node_name):
        return app.getTopicWithID('file:///download/knowledge/jill.xtm#%s' % node_name)

    def noogie(self,app,discard):
        return app.getTopicWithID('file:///home/smurp/src/nooron/catalog.xtm#%s' % discard)
        return app.getTopicWithID('file:///download/knowledge/jill.xtm#%s' % discard)    

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


    def present(self,input):
        if type(input) == type(''):
            return input
        elif type(input) == type([]):
            retarray = []
            for t in input:
                if str(t.__class__) == 'GWApp.TMObject':
                    retarray.append(self.present_tmobject(t))
                else:
                    retarray.append(str(type(t)))
            return string.join(retarray,'<LI>')
        elif str(input.__class__) == 'GWApp.TMObject':
            return self.present_tmobject(input)
        else:
            return str(input)
        

    def handle_request(self,request):
        
        [path, params, query, fragment] = request.split_uri()

        while path and path[0] == '/':
            path = path[1:]

        if '%' in path:
            path = unquote (path)

        path_list = path.split('/')
        header = self.breadcrumbs(path_list) + "<hr>\n"        
        if path_list[-1] == '':
            del path_list[-1]

        if len(path_list) == 1 and path_list[0] == 'map':
            content = self.available_graphs()
            content = content + """
            <hr>
            TBD: show list of available topic maps"""
        elif len(path_list) == 2:
            content = self.available_queries_for_graph(path_list[1])
            content = content + """
            <hr>
            topicmap = %s<br>TBD: show list of available actions (topic,class,scope,etc)""" % path_list[1]
        elif len(path_list) == 3:
            if self.is_query(path_list[2]):
                content = self.do_query(tm_name=path_list[1],query_name=path_list[2])
            else:
                meth_name = path_list[2]
                content = self.graph_query(path_list[1],meth_name)
                if 0:
                    if self.__dict__.has_key(meth_name) and type(self[meth_name]) == type(self.__init__):
                        content = self.query(path_list[1],meth_name)
                        #content = "results of <code>%s()</code> here" % meth_name
                    else:
                        content = "don't know what to do for '%s'" % meth_name
                
            content = content + """
            <hr>
            topicmap = %s<br>
            action=%s<br>
            TBD: show list of available subjects of action
               (e.g. for action=topic: smurp,criterion,evaluation,etc))""" % (path_list[1],path_list[2])
        elif len(path_list) == 4:
            #content = self.do_query(tm_name=path_list[1],query_name=path_list[2],as=path_list[3])
            tm_name = path_list[1]
            meth_name = path_list[2]
            fragment = path_list[3]
            app = self.graphs[tm_name]
            coerce_arg = {'TMObject':int}

            # coerce type of fragment if need be
            if coerce_arg.has_key(meth_name):
                fragment = coerce_arg[meth_name](fragment)

            # cascade attempts to run method
            try:
                meth = getattr(app,meth_name)
                args = [fragment]
            except:
                meth = None
            if not meth:
                try:
                    meth = getattr(self,meth_name)
                    args = [app,fragment]
                except:
                    meth = None
            if meth:
                content = self.present(apply(meth,args,{}))
            else:
                content = " no damn luck finding %s on app or self" % meth_name
            content = content + """
            <hr>
            topicmap = %s<br>
            action=%s<br>
            subject=%s<br>
            TBD: show default html view of the subject
            TBD: show list of available views (html,xtm,atm,svg) or actions (???)""" % (path_list[1],
                                                                                        path_list[2],
                                                                                        path_list[3])
        else:
            content="duh len(path_list) = %i" % len(path_list)

        content = content + "<hr> path_list  = " + str(path_list)

        response =  """<html><head><title>Boo</title></head><body>
        %s
        %s
        <hr>
        <dl>
          <dt>path<dd>%s
          <dt>params<dd>%s
          <dt>query<dd>%s
          <dt>fragment<dd>%s
        </dl>
        <hr>
        timstamp = %s
        </body></html>""" % (header
                             ,content
                             ,str(path),str(params),str(query),str(fragment)
                             ,request.reply_headers['Date']
                             )
        request['Content-Length'] = len(response)
        request.push(response)
        request.done()

    

lg = logger.file_logger (sys.stdout)
fs = filesys.os_filesystem (PUBLISHING_ROOT)
dh = default_handler.default_handler (fs)
ph = post_script_handler (fs)


tmh = topicmap_handler('')
tmh.import_topicmap('jill','file:///download/knowledge/jill.xtm')
tmh.import_topicmap('weblog','file:///home/smurp/src/nooron/weblog.xtm')
tmh.import_topicmap('catalog','file:///home/smurp/src/nooron/catalog.xtm')

#tmh.import_topicmap('opera','file:///download/knowledge/opera.xtm')
#tmh.import_topicmap('nooron','file:///home/smurp/src/nooron/nooron.xtm')

tmh.add_graph('jill',"type=MySQL,name=jill,user=smurp,pass=trivialpw")

#tmh.do_query('jill','instances')

#sys.exit()

hs = http_server.http_server ('', 8081, logger_object = lg)
sh = status_handler.status_extension([hs])
hs.install_handler(sh)


hs.install_handler(dh)
hs.install_handler(ph)
hs.install_handler(tmh)

asyncore.loop()

