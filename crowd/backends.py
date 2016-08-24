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
    This is the Atlassian CROWD (JIRA) Authentication Backend for Django
    Hope you will never need opening this file looking for a bug =)
    """

    def authenticate(self, username=None, password=None, email=None, **kwargs):
        """
        Main authentication method
        Args:
            :param email: Email Address
            :param password: Password
            :param username: UserName
        """
        username = username
        password = password
        email = email
        if (not username and not email) or not password:
            return None
        username = self.get_username_from_email(email or username)
        user = self.find_existing_user(username)

        resp, session_crowd = self._call_crowd_session(username, password)
        if resp == 201:
            logger.debug("got response from Crowd")
            logger.debug(session_crowd)
            if not user:
                logger.debug("Create User")
                user = self.create_user_from_crowd(username)
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

    @staticmethod
    def find_existing_user(username):
        """
        Finds an existing user with provided username. Private service method.
        Args:
            :param username: can be either username or the email
        """

        user_model = get_user_model()
        users = user_model.objects.filter(username=username)
        if users.count() <= 0:
            users = user_model.objects.filter(email=username)
            if users.count() <= 0:
                return None
            else:
                return users[0]
        else:
            return users[0]

    @staticmethod
    def _call_crowd_session(username, password):
        """
        Calls CROWD webservice. Private service method.
        """
        crowd_config = CrowdBackend._get_crowd_config()

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
        except KeyError:
            token = None
        return r.status_code, token

    @staticmethod
    def get_username_from_email(email):
        """
        Check if username is email
        """
        user_model = get_user_model()
        # first look locally
        user = user_model.objects.filter(email=email)
        if user:
            username = user[0].username
            logger.debug("Found in local DB")
            return username

        crowd_config = CrowdBackend._get_crowd_config()

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
    def create_user_from_crowd(username):
        """
        Creating a new user in django auth database basing on
        information provided by CROWD. Private service method.
        """
        crowd_config = CrowdBackend._get_crowd_config()
        username = CrowdBackend.get_username_from_email(username)
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


def import_users_from_email_list(list_of_users):
    new_users = []
    not_found_users = []

    for user in list_of_users:
        print(user)
        user_name = CrowdBackend.get_username_from_email(user)
        if user == user_name:
            not_found_users.append(user)
        else:
            new_users.append(user_name)

    if new_users:
        for name in new_users:
            if not (CrowdBackend.find_existing_user(name)):
                CrowdBackend.create_user_from_crowd(name)
    return new_users, not_found_users


def get_crowd_config():
    """
    Returns CROWD-related project settings. Private service method.
    """
    config = getattr(settings, 'CROWD', None)
    if not config:
        raise UserWarning('CROWD configuration is not in your settings.py')
    return config
