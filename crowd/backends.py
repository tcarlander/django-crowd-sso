from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
import requests
import json
from importlib import import_module
from django.conf import settings
import logging
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
my_timeout = 5

logger = logging.getLogger(__name__)


class CrowdBackend(ModelBackend):
    """
    This is the Attlasian CROWD (JIRA) Authentication Backend for Django
    Hope you will never need opening this file looking for a bug =)
    """

    def authenticate(self, username, password):
        """
        Main authentication method
        """

        logger.debug("Authenticate")
        crowd_config = self._get_crowd_config()
        user = self._find_existing_user(username)
        resp, session_crowd = self._call_crowd_session(username,
                                                       password,
                                                       crowd_config)
        if resp == 201:
            logger.debug("got response")
            print (session_crowd)
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
        users = User.objects.filter(username=username)
        if users.count() <= 0:
            return None
        else:
            return users[0]

    def _call_crowd_session(self, username, password, crowd_config):
        """
        Calls CROWD webservice. Private service method.
        """
        
        url = crowd_config['url'] + ('/usermanagement/latest/session.json')
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
                                   'Accept': 'application/json'},timeout=my_timeout)
        try:
            token = r.json()['token']
        except:
            token = None
        return r.status_code, token
    
    @staticmethod
    def _create_user_from_crowd(username, crowd_config):
        """
        Creating a new user in django auth database basing on
        information provided by CROWD. Private service method.
        """

        url = '%s/usermanagement/latest/user.json?username=%s' % (
            crowd_config['url'], username,)
        r = requests.get(url, auth=(crowd_config['app_name'],
                         crowd_config['password']),timeout=my_timeout)
        content_parsed = r.json()
        user = User.objects.create_user(username, content_parsed['email'])
        user.set_unusable_password()
        user.first_name = content_parsed['first-name']
        user.last_name = content_parsed['last-name']
        user.is_active = True
        user.is_superuser = crowd_config.get('superuser', False)
        user.is_staff = crowd_config.get('staffuser', False)
        user.save()
        return user
