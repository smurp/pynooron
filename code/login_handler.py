"""The login handler provides /logout and /login with redirect."""

import re
import string
import base64
from medusa import default_handler

AUTHORIZATION = re.compile (
        #               scheme  challenge
        'Authorization: ([^ ]+) (.*)',
        re.IGNORECASE
        )

get_header = default_handler.get_header

class login_handler:
    def __init__ (self, authorizer, realm='default'):
        self.authorizer = authorizer
        self.realm = realm
        #self.pass_count = counter.counter()
        #self.fail_count = counter.counter()

    def match (self, request):
        [path, params, query, fragment] = request.split_uri()
        path_list = path.split('/')

        while path_list and path_list[0] == '':
            path_list = path_list[1:]
        return path_list and path_list[0] in ['login','whoami']

    def handle_request(self,request):
        [path, params, query, fragment] = request.split_uri()
        path_list = path.split('/')

        while path_list and path_list[0] == '':
            path_list = path_list[1:]
        if path_list[0] == 'login':
            was = len(path_list) > 1 and path_list[1] or None
            self.handle_login(request,was)
        if path_list[0] == 'logout':
            self.handle_relogin(request)
        if path_list[0] == 'whoami':
            self.handle_whoami(request)

    def handle_login(self,request,was=None):
        scheme = get_header(AUTHORIZATION,request.header)
        if scheme:
            scheme = string.lower(scheme)
            if scheme == 'basic':
                print "scheme is basic"
                cookie = get_header (AUTHORIZATION, request.header, 2)
                try:
                    decoded = base64.decodestring (cookie)
                except:
                    print 'malformed authorization info <%s>' % cookie
                    request.error (400)
                    return
                auth_info = string.split (decoded, ':')
                print auth_info,was
                if auth_info[0] == was:
                    self.finally_handle_login(request)                    
                elif self.authorizer.authorize(auth_info):
                    #self.pass_count.increment()
                    request.auth_info = auth_info
                    #request['Set-Cookie'] = 'foo=bar'
                    #request['Set-Cookie'] = 'blick=boor'
                    request['Location'] = '/whoami'
                    request.error(302)
                    return                     
                else:
                    self.finally_handle_login(request)
            #elif scheme == 'digest':
            #       print 'digest: ',AUTHORIZATION.group(2)
            else:
                print 'unknown/unsupported auth method: %s' % scheme
                self.finally_handle_login(request)
        else:
            self.finally_handle_login(request)


    def handle_relogin(self,request):
        request.channel.set_terminator (None)
        request['Connection'] = 'close'
        request['WWW-Authenticate'] = 'Basic realm="%s"' % self.realm
        request.error (401)

    def finally_handle_login(self,request):
        request.channel.set_terminator (None)
        request['Connection'] = 'close'
        request['WWW-Authenticate'] = 'Basic realm="%s"' % self.realm
        request.error (401)


    def handle_whoami(self,request):
        content = """
<html><head><title>Unauthorized</title></head>
<body>
Whoami
<hr/>
%s
<hr/>
<a href="/">Proceed to site root.</a>
</body>
</html>
        """ % string.join(request.header,"<br/>")

        request['Content-Length'] = len(content)
        request['Content-Type'] = 'text/html'

        if request.command == 'GET':
            request.push (content)
        request.done()

        


class dictionary_authorizer:
    def __init__ (self, dict):
        self.dict = dict

    def authorize (self, auth_info):
        [username, password] = auth_info
        if (self.dict.has_key (username)) and (self.dict[username] == password):
            return 1
        else:
            return 0

