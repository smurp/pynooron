
__version__='$Revision: 1.3 $'[11:-2]
__cvs_id__ ='$Id: http_request_mixin.py,v 1.3 2002/08/07 20:23:41 smurp Exp $'


"""Augment medusa.http_server.http_request with convenience functions.
"""

import re, string
if __name__ == "__main__":
    class http_request:
        pass
else:
    from medusa.http_server import http_request
    from NooronUser import NooronUser, NullUser

def split_uri (self):
    if self._split_uri is None:
        m = self.path_regex.match (self.uri)
        if m.end() != len(self.uri):
            raise ValueError, "Broken URI"
        else:
            self._split_uri = m.groups()
    return self._split_uri
http_request.split_uri = split_uri

def chop_up_query(self,query):
    if not query:
        return {}
    if query[0] != '?':
        raise ValueError, "Broken query"
    assigs = string.splitfields(query[1:],'&')
    retdict = {}
    for assig in assigs:
        pair = string.splitfields(assig,"=")
        if pair and pair[0]:
            if not retdict.has_key(pair[0]):
                retdict[pair[0]] = pair[1]
            else:
                retdict[pair[0]] = [retdict[pair[0]]] + [pair[1]]
    return retdict
http_request.chop_up_query = chop_up_query    

def split_query(self):
    if (not hasattr(self,'_split_query')) or getattr(self,'_split_query') is None:
        query = self.split_uri()[2]
        self._split_query = self.chop_up_query(query)
    return self._split_query
http_request.split_query = split_query


def effective_query(self):
    if (not hasattr(self,'_effective_query')):
        self._effective_query_init()
    return self._effective_query.copy()
http_request.effective_query = effective_query

def _effective_query_init(self):
    query_copy = self.split_query().copy()
    print "query_copy =",query_copy
    self._effective_query = query_copy
    
http_request._effective_query_init = _effective_query_init    

def effective_query_extend(self,incoming):
    if type(incoming) != type({}):
        raise 'ValueError','effective_query_extend expects a dict'
    if not hasattr(self,'_effective_query'):
        self._effective_query_init()
    self._effective_query.update(incoming)
http_request.effective_query_extend = effective_query_extend


def breadcrumbs(self):
    path = self.split_uri()[0]
    if path and path[0] == '/':
        path = path[1:]
    parts = path.split('/')        
    pth = ''
    crumbs = ''
    for part in parts:
        pth = pth + '/' + part
        atag = """<a href="%s">%s</a>""" % (pth,part)
        crumbs = crumbs + ' / ' + atag
    return crumbs
http_request.breadcrumbs = breadcrumbs

def set_user(self,user):
    self._user = user
http_request.set_user = set_user
    
def user(self):
    if (not hasattr(self,'_user')) or getattr(self,'_user') is None:
        self._user = NullUser()
    return self._user
http_request.user = user
        

if __name__ == "__main__":
    errcount = 0
    tests = (("",{}),
             ("?",{}),
             ("?=",{}),
             ("?=&=&=&",{}),
             ("?one=1",{'one':'1'}),
             ("?one=1&two=2",{'one':'1','two':'2'}),
             ("?one=1&two=2&three=",{'one':'1','two':'2','three':''}),
             ("?one=1&two=2&one=ein",{'one':['1','ein'],'two':'2'}))
    for t in tests:
        out =  chop_up_query(None,t[0])
        if cmp(out,t[1]) != 0:
            errcount =+ 1
            print t[0], " did not return ",t[1]
    print "there were %i errors" % errcount
            
        
