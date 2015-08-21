import json
from importlib import import_module
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import requests
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
my_timeout = 5

logger = logging.getLogger(__name__)


class CrowdBackend(ModelBackend):
    """
    This is the Attlasian CROWD (JIRA) Authentication Backend for Django
    Hope you will never need opening this file looking for a bug =)
    """
# http://login.dev.wfptha.org/crowd/rest/usermanagement/1/search?entity-type=user&restriction=email%3Dtobias.carlander%40wfp.org

    def authenticate(self,  **kwargs):
        """
        Main authentication method
        :param **kwargs:
        """
        username = kwargs.get("username")
        password = kwargs.get("password")
        email = kwargs.get("email")
        if(not username and not email) or not password:
                return None
        logger.debug("Authenticate")
        crowd_config = self._get_crowd_config()
        username = self._get_username_from_email(email or username, crowd_config)
        logger.debug(username)
        user = self._find_existing_user(username)

        resp, session_crowd = self._call_crowd_session(username,
                                                       password,
                                                       crowd_config)
        if resp == 201:
            logger.debug("got response")
            logger.debug(session_crowd)
            if not user:
                logger.debug("Create User")
                user = self._create_user_from_crowd(username, crowd_config)
            user.crowdtoken = session_crowd
            return user
        else:
            return None

    @staticmethod
    def _get_crowd_config():
        """
        Returns CROWD-related project settings. Private service method.
        """
        config = getattr(settings, 'CROWD', None)
        if not config:
            raise UserWarning('CROWD configuration is not in your settings.py')
        return config

    def _find_existing_user(self, username):
        """
        Finds an existing user with provided username. Private service method.
        """
        user_model = get_user_model()
        users = user_model.objects.filter(username=username)
        if users.count() <= 0:
            return None
        else:
            return users[0]

    def _call_crowd_session(self, username, password, crowd_config):
        """
        Calls CROWD webservice. Private service method.
        """

        url = crowd_config['url'] + '/usermanagement/latest/session.json'
        json_object = {'username': username,
                       'password': password,
                       'validation-factors':
                       {'validationFactors': [
                           {'name': 'remote_address',
                            'value': crowd_config['validation']}
                       ]}
                       }
        r = requests.post(url,
                          auth=(crowd_config['app_name'],
                                crowd_config['password']),
                          data=json.dumps(json_object),
                          headers={'content-type': 'application/json',
                                   'Accept': 'application/json'}, timeout=my_timeout)
        try:
            token = r.json()['token']
        except:
            token = None
        return r.status_code, token

    @staticmethod
    def _get_username_from_email(email, crowd_config):
        print("Email Test")
        url = '%s/usermanagement/latest/search.json?entity-type=user&restriction=email%%3D%s' % (crowd_config['url'],
                                                                                                 email,)
        r = requests.get(url, auth=(crowd_config['app_name'],
                         crowd_config['password']), timeout=my_timeout)
        content_parsed = r.json()
        try:
            username = content_parsed['users'][0]['name']
        except IndexError:
            username = email
        return username

    @staticmethod
    def _create_user_from_crowd(username, crowd_config):
        """
        Creating a new user in django auth database basing on
        information provided by CROWD. Private service method.
        """
        username = CrowdBackend._get_username_from_email(username, crowd_config)
        url = '%s/usermanagement/latest/user.json?username=%s' % (
            crowd_config['url'], username,)
        r = requests.get(url, auth=(crowd_config['app_name'],
                         crowd_config['password']), timeout=my_timeout)
        content_parsed = r.json()
        user_model = get_user_model()
        user = user_model.objects.create_user(username, content_parsed['email'])
        user.set_unusable_password()
        user.first_name = content_parsed['first-name']
        user.last_name = content_parsed['last-name']
        user.is_active = True
        user.is_superuser = crowd_config.get('superuser', False)
        user.is_staff = crowd_config.get('staffuser', False)
        user.save()
        return user
