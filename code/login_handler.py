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
    def __init__ (self, authorizer, realm='default'):
        self.the_user_id_name = 'the_user_id'
        self.the_user_pw_name = 'the_user_pw'
        self.onsuccess_name = 'OnSuccessRedirTo'
        self.authorizer = authorizer
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
                    print "pair",pair
                    cookie_dict[string.strip(pair[0])]=pair[1]
        return cookie_dict
        
    def authenticate(self,request):
        auth_info = self.get_auth_info_from_cookie(request)
        if not auth_info:
            auth_info = self.get_auth_info_from_form(request)
        print "authenticator ==> auth_info",auth_info
        if self.authorizer.authorize(auth_info):
            self.set_auth_cookies(request,auth_info)
            return auth_info
        return []

    def set_auth_cookies(self,request,auth_info):
        request['Set-Cookie'] = ['%s=%s' % (self.the_user_id_name,
                                           auth_info[0]),
                                 '%s=%s' % (self.the_user_pw_name,
                                           auth_info[1])]



    def handle_logout(self,request):
        request['Set-Cookie'] = '%s=; %s' % \
                                (self.the_user_pw_name,
                                 'expires=Wednesday, 09-Nov-71 23:12:40 GMT')
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
        print "cookies",cookies
        if cookies:
            the_user_id = cookies.get(self.the_user_id_name)
            the_user_pw = cookies.get(self.the_user_pw_name)
            print "raw",the_user_id,the_user_pw
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
        request._auth_info = self.authenticate(request)

        if not request._auth_info:
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
        <a href="/whoami">/whoami</a>
        </body>
        </html>
        """ % (request._auth_info and request._auth_info[0],
               """ <input type="hidden" name="OnSuccessRedirTo" value="/"/> """)
        request['Content-Length'] = len(content)
        request['Content-Type'] = 'text/html'
        #if request.command == 'GET':
        #    request.push (content)
        request.push(content)
        request.done()


    def handle_whoami(self,request):
        content = """
<html><head><title>Unauthorized</title></head>
<body>
Whoami
<hr/>
%s
<hr/>
<a href="/">Proceed to site root.</a><br/>
<a href="/login">/login</a><br/>
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
        try:
            [username, password] = auth_info
            if (self.dict.has_key (username)) and \
                   (self.dict[username] == password):
                return 1
        except:
            return 0
        return 0

