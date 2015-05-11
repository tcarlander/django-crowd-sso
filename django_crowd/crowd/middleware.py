from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login, logout
from datetime import datetime, timedelta
from .backends import CrowdBackend
from importlib import import_module
from django.conf import settings
import logging
import requests
my_timeout = 5
logger = logging.getLogger(__name__)


class CrowdMiddleware(object):
    """Authentication Middleware for OpenAM using a cookie with a token.
    Backend will get user.
    """
    cookie_configd = False
    cookie_name = ''
    cookie_domain = ''
    cookie_secure = False

    def process_request(self, request):
#        CrowdBackend =  CrowdBackend()
        self.cookie_config()
        username = None
        CRCN = CrowdBackend.__module__+"." + CrowdBackend.__name__
        crowd_token = request.COOKIES.get(self.cookie_name,None)

        if not crowd_token:
            logger.debug("Should logout or am i local")
            sess = request.session.get('CrowdToken',None)
            if sess is not None:
                request.session.flush()
                logger.debug("Logout due to Crowd SSO logout")
            return

        if crowd_token:
            request.session['CrowdToken'] = crowd_token
            request.session.save()
            username,status_code_token = self.get_the_user_from_token(crowd_token)
            if not(status_code_token) :
                request.session.flush()
            
        if request.user.is_authenticated():
            return

        if username:
            logger.debug("Check if User already there")
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                logger.debug("User not yet imported")
                crowd_config = CrowdBackend._get_crowd_config()
                user = CrowdBackend._create_user_from_crowd(
                        username, crowd_config)
            user.backend = CRCN

            request.user = user
        else:
            return
        #CrowdBackend.set_cookie(crowd_token,user)
        login(request, None)

    def process_response(self, request, response):
        CRCN = CrowdBackend.__module__+"." + CrowdBackend.__name__
        crowd_token = request.COOKIES.get(self.cookie_name,None)
        try:
            backend = request.user.backend
        except:
            backend = None
        
        logger.debug("Backend:%s" % backend)
        sess = request.session.get('CrowdToken',None)
        logger.debug("Session:%s" % sess)
        try:
            logged_in = request.user.is_authenticated()
        except:
            logged_in = False
        if logged_in and crowd_token is None and backend == CRCN:
            logger.debug('Manual Login with Crowd (need to set cookie)')
            self.cookie_config()
            crowd_token = request.user.crowdtoken
            username,status_code_token = self.get_the_user_from_token(crowd_token)
            
            logger.debug("only crowd:%s" % username)
            if username and status_code_token :
                response.set_cookie(self.cookie_name,
                                    crowd_token,
                                    max_age=None,
                                    expires=None,
                                    domain=self.cookie_domain,
                                    path="/",
                                    secure=self.cookie_secure)
                logger.debug(self.cookie_domain)
            else:
                logout(request) #How would i Get here?
                
            if sess is not None:
                logger.debug("Can i get here?")
                logout(request)

        else:
            if (not(logged_in) and
                    crowd_token is not None):
                self.invalidate_token(crowd_token)
                self.cookie_config()
                response.delete_cookie(self.cookie_name,
                                       domain=self.cookie_domain,
                                       path="/")
        return response


    def invalidate_token(self, token):
        crowd_config = CrowdBackend._get_crowd_config()
        if token:
            url = '%s/usermanagement/latest/session/%s.json' % (
                        crowd_config['url'], token, )
            try:
                r = requests.delete(url, auth=(crowd_config['app_name'],
                                crowd_config['password']),timeout=my_timeout)
            except:
                reqeust.debug('Crowd not responding')
                None

    def get_the_user_from_token(self, token):
#        try:
            crowd_config = CrowdBackend._get_crowd_config()
            url = '%s/usermanagement/latest/session/%s.json' % (
                        crowd_config['url'], token, )
            r = requests.get(url, auth=(crowd_config['app_name'],
                             crowd_config['password']))#,timeout=my_timeout)
            if r.status_code == 200 or r.status_code == 201 :
                content_parsed = r.json()
                return content_parsed['user']['name'],True
            else:
                return None,False
 #        except:
#             logger.error("Can not validate the Token")
#             return None,False

    def cookie_config(self):
        if self.cookie_configd:
            return
        else:
#            try: 
            crowd_config = CrowdBackend._get_crowd_config()
            url = '%s/usermanagement/latest/config/cookie.json' % (
                    crowd_config['url'],)
            r = requests.get(url, auth=(crowd_config['app_name'],
                             crowd_config['password']),timeout=my_timeout)
            content_parsed = r.json()
            self.cookie_name = content_parsed['name']
            self.cookie_domain = content_parsed['domain']
            self.cookie_secure = content_parsed['secure']
            self.cookie_configd = True
 #            except:
#                 logger.error('Can not get Crowd Cookie Config')
#                 return