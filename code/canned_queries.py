


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

    def available_queries_for_graph(self,tm_name):
        query_names = self.canned_queries.keys()
        retval = "<h3>available queries</h3>"
        for n in query_names:
            retval = retval + """<a href="%s">%s</a><br>\n""" % (n,n)
        return retval

    def is_query(self,query_name):
        return self.canned_queries.has_key(query_name)
