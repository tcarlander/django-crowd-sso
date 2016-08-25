import logging
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import requests

from .backends import CrowdBackend, get_crowd_config

my_timeout = 20
logger = logging.getLogger(__name__)


class CrowdMiddleware(object):
    """Authentication Middleware for OpenAM using a cookie with a token.
    Backend will get user.
    """

    cookie_config_done = False
    cookie_name = ''
    cookie_domain = ''
    cookie_secure = False

    def process_request(self, request):  # pragma: no cover

        crowd_config = get_crowd_config()
        try:
            sso = crowd_config['sso']
        except KeyError:
            sso = False
        if not sso:
            return
        self.cookie_config()
        username = None
        crowd_backend_class = CrowdBackend.__module__ + "." + CrowdBackend.__name__
        crowd_token = request.COOKIES.get(self.cookie_name, None)

        if not crowd_token: # pragma: no cover
            logger.debug("Should logout or am i local")
            sess = request.session.get('CrowdToken', None)
            if sess is not None:
                request.session.flush()
                logger.debug("Logout due to Crowd SSO logout")
            return

        if crowd_token: # pragma: no cover
            current_token = request.session.get('CrowdToken')
            if current_token != crowd_token:
                request.session['CrowdToken'] = crowd_token
                # noinspection PyBroadException
                try:
                    with transaction.atomic():
                        request.session.save()
                except:
                    logger.debug("Not saved now")

            username, status_code_token = self.get_the_user_from_token(crowd_token)
            if not status_code_token:
                request.session.flush()

        if request.user.is_authenticated(): # pragma: no cover
            return

        if username: # pragma: no cover
            logger.debug("Check if User already there")
            try:
                user_model = get_user_model()
                user = user_model.objects.get(username=username)
            except ObjectDoesNotExist:
                logger.debug("User not yet imported")
                user = CrowdBackend.create_user_from_crowd(username)
            user.backend = crowd_backend_class

            request.user = user
        else:
            return
        # CrowdBackend.set_cookie(crowd_token,user)
        login(request, None)

    def process_response(self, request, response):  # pragma: no cover
        crowd_config = get_crowd_config()
        try:
            sso = crowd_config['sso']
        except KeyError:
            sso = False
        if not sso:
            logger.debug("No SSO")
            return response

        logger.debug("SSO")
        crowd_backend_class = CrowdBackend.__module__ + "." + CrowdBackend.__name__
        crowd_token = request.COOKIES.get(self.cookie_name, None)
        try:
            backend = request.user.backend
        except AttributeError:
            backend = None

        logger.debug("Backend:%s" % backend)
        sess = request.session.get('CrowdToken', None)
        logger.debug("Session:%s" % sess)
        logged_in = request.user.is_authenticated()
        if logged_in and crowd_token is None and backend == crowd_backend_class:
            logger.debug('Manual Login with Crowd (need to set cookie)')
            self.cookie_config()
            crowd_token = request.user.crowdtoken
            username, status_code_token = self.get_the_user_from_token(crowd_token)

            logger.debug("only crowd:%s" % username)
            if username and status_code_token:
                response.set_cookie(self.cookie_name,
                                    crowd_token,
                                    max_age=None,
                                    expires=None,
                                    domain=self.cookie_domain,
                                    path="/",
                                    secure=self.cookie_secure)
                logger.debug(self.cookie_domain)
            else:
                logout(request)  # How would i Get here?

            if sess is not None:
                logger.debug("Can i get here?")
                logout(request)

        else:
            if (not logged_in and
                    crowd_token is not None):
                self.invalidate_token(crowd_token)
                self.cookie_config()
                response.delete_cookie(self.cookie_name,
                                       domain=self.cookie_domain,
                                       path="/")
        return response

    @staticmethod
    def invalidate_token(token):  # pragma: no cover
        crowd_config = get_crowd_config()
        if token:
            url = '%s/usermanagement/latest/session/%s.json' % (
                crowd_config['url'], token,)
            try:
                requests.delete(url, auth=(crowd_config['app_name'],
                                           crowd_config['password']), timeout=my_timeout)
            except requests.exceptions.Timeout:
                logging.debug('Crowd not responding')

    @staticmethod
    def get_the_user_from_token(token):  # pragma: no cover
        #        try:
        crowd_config = get_crowd_config()
        url = '%s/usermanagement/latest/session/%s.json' % (
            crowd_config['url'], token,)
        r = requests.get(url, auth=(crowd_config['app_name'],
                                    crowd_config['password']))  # ,timeout=my_timeout)
        if r.status_code == 200 or r.status_code == 201:
            content_parsed = r.json()
            return content_parsed['user']['name'], True
        else:
            return None, False

    def cookie_config(self):  # pragma: no cover
        if self.cookie_config_done:
            return
        else:
            crowd_config = get_crowd_config()
            url = '%s/usermanagement/latest/config/cookie.json' % (
                crowd_config['url'],)
            r = requests.get(url, auth=(crowd_config['app_name'],
                                        crowd_config['password']), timeout=my_timeout)
            content_parsed = r.json()
            self.cookie_name = content_parsed['name']
            self.cookie_domain = content_parsed['domain']
            self.cookie_secure = content_parsed['secure']
            self.cookie_config_done = True
