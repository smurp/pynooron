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

COOKIE = re.compile (
        #               scheme  challenge
        'Cookie: (.*)',
        re.IGNORECASE
        )

get_header = default_handler.get_header


class login_handler:
    def __init__ (self, authenticator, realm='default'):
        self.the_user_id_name = 'the_user_id'
        self.the_user_pw_name = 'the_user_pw'
        self.onsuccess_name = 'OnSuccessRedirTo'
        self.authenticator = authenticator
        self.realm = realm
        #self.pass_count = counter.counter()
        #self.fail_count = counter.counter()

    def match (self, request):
        [path, params, query, fragment] = request.split_uri()
        path_list = path.split('/')

        while path_list and path_list[0] == '':
            path_list = path_list[1:]
        return path_list and path_list[0] in ['login','whoami','logout']

    def handle_request(self,request):
        [path, params, query, fragment] = request.split_uri()
        path_list = path.split('/')

        while path_list and path_list[0] == '':
            path_list = path_list[1:]
        if path_list[0] == 'login':
            self.handle_login(request)
        if path_list[0] == 'logout':
            self.handle_logout(request)
        if path_list[0] == 'whoami':
            self.handle_whoami(request)

    def get_cookies_as_dict(self,request):
        cookie_dict = {}
        cookie_str = get_header(COOKIE,request.header)
        if cookie_str:
            cookie_list = string.split(cookie_str,';')
            for name_val in cookie_list:
                pair = string.split(name_val,'=')
                if len(pair) == 2:
                    #print "pair",pair
                    cookie_dict[string.strip(pair[0])]=pair[1]
        #print "get_cookies_as_dict: cookie_dict =",cookie_dict
        return cookie_dict
        
    def authenticate(self,request):
        dude = AnonymousUser
        auth_info = self.get_auth_info_from_cookie(request)
        #print "authenticate: auth_info =",auth_info
        if not auth_info:
            try_to_set_cookies = 1
            auth_info = self.get_auth_info_from_form(request)
        else:
            try_to_set_cookies = 0
        dude = self.authenticator.authenticate(auth_info)
        if try_to_set_cookies and dude != AnonymousUser:
            self.set_auth_cookies(request,auth_info)
        #print "authenticate: dude =",dude
        return dude

    def set_auth_cookies(self,request,auth_info):
        if len(auth_info) == 2:
            request['Set-Cookie'] = ['%s=%s' % (self.the_user_id_name,
                                                auth_info[0]),
                                     '%s=%s' % (self.the_user_pw_name,
                                                auth_info[1])]

    def set_cookies_for_logout(self,request):
        request['Set-Cookie'] = '%s=; %s' % \
                                (self.the_user_pw_name,
                                 'expires=Wednesday, 09-Nov-71 23:12:40 GMT')

    def handle_logout(self,request):
        self.set_cookies_for_logout(request)
        onsuccess = request.form().get(self.onsuccess_name)
        if onsuccess and onsuccess[0]:
            request['Location'] = onsuccess[0]
        else:
            request['Location'] = '/whoami'
        request.error(302)
        return

    def get_auth_info_from_cookie(self,request):
        auth_info = []
        cookies = self.get_cookies_as_dict(request)
        #print "cookies",cookies
        if cookies:
            the_user_id = cookies.get(self.the_user_id_name)
            the_user_pw = cookies.get(self.the_user_pw_name)
            #print "raw",the_user_id,the_user_pw
            if the_user_id != None and the_user_pw != None:
                auth_info = [the_user_id,the_user_pw]
        return auth_info

    def get_auth_info_from_form(self,request):
        auth_info = []
        form = request.form()
        if form:
            the_user_id = form.get('the_user_id')
            the_user_pw = form.get('the_user_pw')
            if the_user_id and the_user_pw :
                auth_info = [the_user_id[0],the_user_pw[0]]
        return auth_info        

    def handle_login(self,request):
        request.AUTHENTICATED_USER = self.authenticate(request)

        if request.AUTHENTICATED_USER == AnonymousUser:
            self.present_login_form(request)
        else:
            onsuccess = request.form().get(self.onsuccess_name)
            if onsuccess and onsuccess[0]:
                request['Location'] = onsuccess[0]
            else:
                request['Location'] = '/whoami'
            request.error(302)
            return

    def present_login_form(self,request):
        content = """<html><head><title>Login</title></head>
        <body>
        <b>%s</b>
        <form>
        UserName: <input name="the_user_id" type="text"/><br/>
        Password: <input name="the_user_pw" type="text"/><br/>
        %s
        <input type="submit" name="Login"/>
        </form>

        <hr/>
        <a href="/">/(root)</a><br/>
        <a href="/login">/login</a><br/>
        <a href="/logout">/logout</a><br/>        
        <a href="/whoami">/whoami</a><br/>        
        </body>
        </html>
        """ % (request.AUTHENTICATED_USER,
               """ <input type="hidden" name="OnSuccessRedirTo" value="/"/> """)
        request['Content-Length'] = len(content)
        request['Content-Type'] = 'text/html'
        #if request.command == 'GET':
        #    request.push (content)
        request.push(content)
        request.done()


    def handle_whoami(self,request):
        user_details = request.has_key('AUTHENTICATED_USER') and \
                       repr(request.AUTHENTICATED_USER) or ''
        content = """
<html><head><title>Who Am I?</title></head>
<body>
Whoami
<hr/>
%s
<hr/>
%s
<hr/>
        <a href="/">/(root)</a><br/>
        <a href="/login">/login</a><br/>
        <a href="/logout">/logout</a><br/>        
        <a href="/whoami">/whoami</a><br/>        
         
</body>
</html>
""" % (string.join(request.header,"<br/>"),
       user_details)

        request['Content-Length'] = len(content)
        request['Content-Type'] = 'text/html'

        if request.command == 'GET':
            request.push (content)
        request.done()

        
from AuthenticatedUser import AuthenticatedUser,AnonymousUser

class dictionary_authenticator:
    def __init__ (self, dict):
        self.dict = dict

    def authenticate (self, auth_info):
        dude = AnonymousUser
        try:
            [username, password] = auth_info
            if (self.dict.has_key (username)) and \
                   (self.dict[username] == password):
                dude = AuthenticatedUser(username)
        except:
            pass 
        return dude

import xmlrpclib

class friendly_favors_authenticator:
    def __init__(self,
                 group_key_map={},
                 fqdn=None,
                 server = 'http://www.favors.org/ffVerify.php'):
        self._server_name = server
        self._server = xmlrpclib.Server(self._server_name)
        self._group_key_map = group_key_map
        self._cache = {}
        self._fqdn = fqdn

    def _do_auth(self,auth_info):
        dude = AnonymousUser
        standard = {}        
        for group in self._group_key_map.items():
            try:
                resp = self._server.ff.startUserSession(auth_info[0],
                                       auth_info[1],  #passwd
                                       group[0],      #favors group
                                       self._fqdn,
                                       group[1])      #group key
                if resp['group_status'] != 'Active':
                    raise 'FriendlyFavorsGroupInactive',\
                          "group:%s status:%s" % (group[0],
                                                  resp['group_status'])
                for fromkey,tokey in {'name':'FullName',
                                      'firstname':'FirstName',
                                      'lastname':'LastName'}.items():
                    if resp.has_key(fromkey):
                        standard[tokey] = resp[fromkey]
                        del resp[fromkey]
                #print "standard:",standard
                #print "resp:",resp                    
                dude = AuthenticatedUser(auth_info[0],
                                         standard,resp,self.__class__)
                break
            except xmlrpclib.Fault:
                continue
        return dude
        
    def authenticate(self,auth_info):
        dude = AnonymousUser
        credentials = str(auth_info)
        #print "ff.authenticate: credentials =",credentials
        if len(auth_info) == 2:
            if self._cache.has_key(credentials):
                #print "cache hit:",credentials
                dude = self._cache[credentials]
                return dude
            else:
                dude = self._do_auth(auth_info)

        if dude != AnonymousUser:
            #print "caching",credentials,'as',dude
            self._cache[credentials] = dude
        return dude

class bogus_favors_authenticator(friendly_favors_authenticator):
    def _do_auth(self,auth_info):
        dude = AnonymousUser
        if len(auth_info) > 1 \
               and auth_info[0] == 'jrl' \
               and auth_info[1] == 'badpw':
            dude =  AuthenticatedUser(auth_info[0],
                                      {'FullName':'J. Random Luser',
                                       'FirstName':'James',
                                       'LastName':'Luser'},
                                      {},self.__class__)
        return dude

class local_identity_authenticator:
    def __init__(self,connection=None,place=None,path=[]):
        if connection:
            self._connection = connection
        elif place:
            initargs = {'default_place':place}
            self._connection = establish_connection(FileSystemConnection,
                                                    initargs)
        
        
