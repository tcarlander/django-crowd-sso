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


class CookieMiddleware(object):
    """Authentication Middleware for OpenAM using a cookie with a token.
    Backend will get user.
    """
    cookie_configd = False
    cookie_name = ''
    cookie_domain = ''
    cookie_secure = False

    def process_request(self, request):
        self.cookie_config()
        username = None
        try:
            CrowdBackend.set_ip(request.META['HTTP_X_FORWARDED_FOR'])
        except:
            CrowdBackend.set_ip(request.META['REMOTE_ADDR'])
        if self.cookie_name not in request.COOKIES:
            logger.debug("Should logout or am i local")
            try:
                sess = request.session['CrowdToken']
            except:
                sess = None
            if sess is not None:
                request.session.flush()
                logger.debug("Logout due to Crowd SSO logout")
            return

        crowd_token = request.COOKIES[self.cookie_name]
        if crowd_token:
            request.session['CrowdToken'] = crowd_token
            request.session.save()
            username = self.get_the_user_from_token(crowd_token)
        if request.user.is_authenticated():
            return
        if username:
            try:
                user = User.objects.filter(username=username)[0]
                user.backend = 'crowd.backends.CrowdBackend'
                request.user = user
            except:
                # If User not yet imported
                crowd_config = CrowdBackend._get_crowd_config(self)
                user = CrowdBackend._create_user_from_crowd(
                       CrowdBackend, username, crowd_config)
                user.backend = 'crowd.backends.CrowdBackend'
                request.user = user
        else:
            return
        CrowdBackend.set_cookie(crowd_token)
        login(request, None)

    def process_response(self, request, response):
        try:
            crowd_token = request.COOKIES[self.cookie_name]
        except KeyError:
            crowd_token = None
        try:
            backend = request.user.backend
        except:
            backend = None
        logger.debug("Backend:%s" % (backend,))
        try:
            sess = request.session['CrowdToken']
        except:
            sess = None
        logger.debug("Session:%s" % sess)
        try:
            if request.user.is_authenticated() and crowd_token is None:
                if backend == 'crowd.backends.CrowdBackend':
                    self.cookie_config()
                    crowd_token = CrowdBackend.get_cookie()
                    username = self.get_the_user_from_token(crowd_token)
                    logger.debug("only crowd:%s" % (username,))
                    if username:
                        response.set_cookie(self.cookie_name,
                                            crowd_token,
                                            max_age=None,
                                            expires=None,
                                            domain=self.cookie_domain,
                                            path="/",
                                            secure=self.cookie_secure)
                        logger.debug(self.cookie_domain)
                    CrowdBackend.set_cookie(None)

                if sess is not None:
                    logger.debug("Can i get here?")
                    logout(request)

            else:
                if (not(request.user.is_authenticated()) and
                        crowd_token is not None):
                    self.invalidate_token(crowd_token)
                    CrowdBackend.destroy_cookie()
                    self.cookie_config()
                    response.delete_cookie(self.cookie_name,
                                           domain=self.cookie_domain,
                                           path="/")
        except:
            None
        return response

    def invalidate_token(self, token):
        crowd_config = CrowdBackend._get_crowd_config(self)
        if token:
            url = '%s/usermanagement/latest/session/%s.json' % (
                        crowd_config['url'], token, )
            try:
                r = requests.delete(url, auth=(crowd_config['app_name'],
                                crowd_config['password']),timeout=my_timeout)
            except:
                None

    def get_the_user_from_token(self, token):
        try:
            crowd_config = CrowdBackend._get_crowd_config(self)
            url = '%s/usermanagement/latest/session/%s.json' % (
                        crowd_config['url'], token, )
            r = requests.get(url, auth=(crowd_config['app_name'],
                             crowd_config['password']),timeout=my_timeout)
            if r.status_code < 300:
                content_parsed = r.json()
                return content_parsed['user']['name']
            else:
                return None
        except:
            return None


    def cookie_config(self):
        if self.cookie_configd:
            return
        else:
            try: 
                crowd_config = CrowdBackend._get_crowd_config(self)
                url = '%s/usermanagement/latest/config/cookie.json' % (
                        crowd_config['url'],)
                r = requests.get(url, auth=(crowd_config['app_name'],
                                 crowd_config['password']),timeout=my_timeout)
                content_parsed = r.json()
                self.cookie_name = content_parsed['name']
                self.cookie_domain = content_parsed['domain']
                self.cookie_secure = content_parsed['secure']
                self.cookie_configd = True
            except:
                return