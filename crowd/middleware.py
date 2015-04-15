from django.contrib.auth.models import User
from django.conf import settings
from xml.dom.minidom import parseString
from django.contrib.auth import authenticate, login
import httplib2
from crowd.backends import CrowdBackend

class CookieMiddleware( object ):
    """Authentication Middleware for OpenAM using a cookie with a token.
    Backend will get user.
    """
    def process_request(self, request):
    
        if "crowd.token_key" not in request.COOKIES:
            return
        token= request.COOKIES["crowd.token_key"]
        username = self.get_the_user_from_token(token)
        if username :
            try:
                user = User.objects.filter(username=username)[0]
                user.backend = 'crowd.backends.CrowdBackend'
                request.user = user
            except:
                #User not yet imported
                crowd_config = CrowdBackend._get_crowd_config(self)
                user = CrowdBackend._create_new_user_from_crowd_response(CrowdBackend,username,crowd_config)
                user.backend = 'crowd.backends.CrowdBackend'
                request.user = user
        else:
            #session Invalid
            return
            
        login(request, None)



    def get_the_user_from_token(self,token):
        crowd_config = CrowdBackend._get_crowd_config(self)
        h = httplib2.Http()
        h.add_credentials(crowd_config['app_name'], crowd_config['password'])
        url = crowd_config['url'] + ('/usermanagement/latest/session/%s'% (token,))
        resp, content = h.request(url, "GET")
        if resp.status < 400:
            content_parsed = CrowdBackend._parse_crowd_response(content)
        else:
            return None
        return content_parsed['user']
