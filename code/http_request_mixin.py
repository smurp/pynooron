
__version__='$Revision: 1.16 $'[11:-2]
__cvs_id__ ='$Id: http_request_mixin.py,v 1.16 2003/04/24 11:07:36 smurp Exp $'


"""Augment medusa.http_server.http_request with convenience functions.
"""
from settings import *
import re, string, sys
import traceback
import cgi

if __name__ == "__main__":
    class http_request:
        pass
else:
    from medusa.http_server import http_request
    from medusa.http_server import http_server
    from NooronUser import NooronUser, NullUser


http_request.__allow_access_to_unprotected_subobjects__ = 1


def absolute_url(server):
    default_name = str(server.ip)
    if server.port != 80:
        default_name += ':' + str(server.port)
    retval = '://'+(server.server_name or default_name)
    return retval
http_server.absolute_url = absolute_url

def split_uri (self):
    if self._split_uri is None:
        m = self.path_regex.match (self.uri)
        if m.end() != len(self.uri):
            raise ValueError, "Broken URI"
        else:
            self._split_uri = m.groups()
    return self._split_uri
http_request.split_uri = split_uri

def reply_headers_items(self):
    items = self.reply_headers.items()
    ret_items = []
    lst = type([])
    for item in items:
        if type(item[1]) == lst:
            for val in item[1]:
                ret_items.append((item[0],val))
        else:
            ret_items.append(item)
    return ret_items
http_request.reply_headers_items = reply_headers_items

def build_reply_header (self):
    return string.join (
        [self.response(self.reply_code)] + \
        map(lambda x: '%s: %s' % x, self.reply_headers_items()),
        '\r\n') + '\r\n\r\n'
http_request.build_reply_header=build_reply_header

def form(self):
    if not self.__dict__.has_key('_form'):
        query = self.split_uri()[2]
        self._form = cgi.parse_qs(query and query[1:] or '',
                                  keep_blank_values=1)
    return self._form
http_request.form = form

################################
def set_object_request(request,object_request):
    request._object_request = object_request
http_request.set_object_request = set_object_request
def object_request(self):
    return self.__dict__.get('_object_request')
http_request.object_request = object_request

################################
def set_base_request(request,base_request):
    request._base_request = base_request
http_request.set_base_request = set_base_request
def base_request(self):
    """The base_request fully specifies the object and garment to publish.
    It is the path the user could (or might) have
    visited to be explicit about which GARMENT to use.  If the
    actual_request is not a base_request (bacause it does not specify
    a garment) then some algorithm (such
    as pick-the-first-possible-garment-which-produces-.html) is
    used to determine the base_request.  Notice that no transforming
    or encoding extensions (such as .ps, .pdf, .gz) are included.
    THING__GARMENT  eg /know/nooron_faq/faq__details.html"""
    return self.__dict__.get('_base_request','')
http_request.base_request = base_request

################################
def name_request(request):
    """The name_request is just the pathless name of the object
    plus the name of the garment, without ANY extensions.

    Motivation:
       Handy for naming graphviz graphs.
    Examples:
       nooron_pert___aon
       """
    br = request.base_request()
    slashes = string.split(br,'/')
    return string.split(slashes[-1],'.')[0]
http_request.name_request = name_request

################################
def name_of_garmie(request):
    """The name of the garment (including its one native extension).
    
    Motivation:
       Handy for comparing with other available garments.
    Examples:
       aon.dot
       """
    br = request.base_request()
    wedgies = string.split(br,wedge_string)
    return wedgies[-1]
http_request.name_of_garmie = name_of_garmie

################################
def set_kb_request(request,kb_request):
    request._kb_request = kb_request
http_request.set_kb_request = set_kb_request
def kb_request(self):
    return self.__dict__.get('_kb_request','')
http_request.kb_request = kb_request

################################
def set_canonical_request(request,canonical_request):
    request._canonical_request = canonical_request
http_request.set_canonical_request = set_canonical_request
def canonical_request(self):
    return self.__dict__.get('_canonical_request')
http_request.canonical_request = canonical_request



################################
def set_header(self,key,val):
    self.reply_headers[key]=val
http_request.set_header = set_header

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
        pth = pth + '/' + part # + '/'
        # lets break out a link to here
        if string.find(part,wedge_string) > 0:
            # yes 0, in case the name of the thing is of length 1
            here_name,garm_name = string.split(part,wedge_string,2)
            garm_path = pth
            shorten_by = len(garm_name) + len(wedge_string)
            here_path = garm_path[:-1 * shorten_by]
            here_link = """<a href="%s">%s</a>""" % (here_path,here_name)
            garm_link = """<a href="%s">%s</a>""" % (garm_path,garm_name)
            crumbs = crumbs + '&nbsp;/&nbsp;' + here_link +\
                     ' ' + wedge_string + ' ' + garm_link
        else:
            atag = """<a href="%s">%s</a>""" % (pth,part)
            crumbs = crumbs + '&nbsp;/&nbsp;' + atag
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

def instrumented_getattr(me,key):
    #print key
    if str(key) == "__allow_access_to_unprotected_subobjects__":
        #print "NOW WE HAVE IT!"
        try:
            raise "Booger!","snort"
        except:
            #print "NOW PRINT STACK FRAME!", traceback.print_stack()
            pass
    return me.__dict__.get_attr(key)
#http_request.__getattr__ = instrumented_getattr

def error(self,code,message=None,tb=None):
    self.reply_code = code
    if not message: message = self.responses[code]
    if 1:
        (errtype,errval,t) = sys.exc_info()
        tb = traceback.format_tb(t,15)
        message = message + "\n<hr>"+ "\n<b>%s</b><br>%s<pre>%s</pre>" % \
                  (errtype,errval,string.join(tb,"\n"))
    s = self.DEFAULT_ERROR_MESSAGE % {
        'code': code,
        'message': message,
        }
    self['Content-Length'] = len(s)
    self['Content-Type'] = 'text/html'
    # make an error reply
    self.push (s)
    self.done()
http_request.error = error

# /usr/local/zope/Zope-2.5.1/lib/python/AccessControl/ZopeSecurityPolicy.py
http_request.__roles__ = None
http_request.__allow_access_to_unprotected_subobjects__ = 1

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
            
        
