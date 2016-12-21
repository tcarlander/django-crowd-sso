import json
from importlib import import_module
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import requests
from django.conf import settings
from django.contrib.auth.models import Group
from requests.exceptions import ConnectionError

try:
    from tenant_schemas import get_public_schema_name
    from tenant_schemas.utils import schema_context
    ts_installed = True
except:
    ts_installed = False


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
            crowd_config = get_crowd_config()
            group_name = crowd_config.get('crowd_group', 'CrowdUser')
            if ts_installed and not (crowd_config.get('DTS_not_use_public_schema', 'CrowdUser')):
                with schema_context(get_public_schema_name()):
                    if user.groups.filter(name=group_name).exists():
                        pass
                    else:
                        crowd_group, created = Group.objects.get_or_create(name=group_name)
                        user.groups.add(crowd_group)
                        user.save()
            else:
                if user.groups.filter(name=group_name).exists():
                    pass
                else:
                    crowd_group, created = Group.objects.get_or_create(name=group_name)
                    user.groups.add(crowd_group)
                    user.save()
            return user
        else:
            return None

    @staticmethod
    def find_existing_user(username):
        """
        Return an existing user with provided username/email.

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
    def _call_crowd_session(username: str, password: str):
        """
        Calls CROWD to authenticate user, return CROWD Token and return code
        CROWD Token will be None if failed to authenticate and if the crowd server is not reachable
        :rtype: (string, string)
        :return: (status_code, token)
        """
        crowd_config = get_crowd_config()
        url = crowd_config['url'] + '/usermanagement/latest/session.json'
        json_object = {'username': username,
                       'password': password,
                       'validation-factors':
                           {'validationFactors': [
                               {'name': 'remote_address',
                                'value': crowd_config['validation']}
                           ]}
                       }
        try:
            r = requests.post(url,
                          auth=(crowd_config['app_name'],
                                crowd_config['password']),
                          data=json.dumps(json_object),
                          headers={'content-type': 'application/json',
                                   'Accept': 'application/json'}, timeout=my_timeout)
            token = r.json()['token']
        except (ConnectionError, KeyError) as e:
            return 503, None
        return r.status_code, token

    @staticmethod
    def get_username_from_email(email: str):
        """
        Check if this emails is a known user (in django users or in crowd) and passes username back if found
        If not found in crowd pass back the incoming string
        """
        user_model = get_user_model()
        # first look locally
        user = user_model.objects.filter(email=email)
        if user:
            username = user[0].username
            logger.debug("Found in local DB")
            return username

        crowd_config = get_crowd_config()

        url = '%s/usermanagement/latest/search.json?entity-type=user&restriction=email%%3D%s' % (crowd_config['url'], email,)
        r = requests.get(url, auth=(crowd_config['app_name'],
                                    crowd_config['password']), timeout=my_timeout)
        content_parsed = r.json()
        try:
            username = content_parsed['users'][0]['name']
        except IndexError:
            username = email
        return username

    @staticmethod
    def create_user_from_crowd(username: str):
        """
        Creating a new user in django auth database basing on
        information provided by CROWD. Private service method.
        """
        crowd_config = get_crowd_config()
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
        group_name = crowd_config.get('crowd_group', 'CrowdUser')

        if ts_installed and not(crowd_config.get('DTS_not_use_public_schema', 'CrowdUser')):
            with schema_context(get_public_schema_name()):
                crowd_group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(crowd_group)
                user.save()
        else:
            crowd_group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(crowd_group)
            user.save()
        return user


def import_users_from_email_list(list_of_emails):
    """
    Takes an array of emails and returns a tuple with:
        Usernames of Users found in django users or found and imported from crowd to django users
        emails not found in either django users or in crowd
    
    :rtype: (list[string], list[string],list[string])
    :param list_of_emails: list[string]
    """
    found_and_added_users = []
    not_found_emails = []
    not_allowed_emails = []
    crowd_config = get_crowd_config()
    domains_not_allowed = crowd_config.get('disallowed_creation_domains', ['@wfp.org'])
    for email in list_of_emails:
        user_name = CrowdBackend.get_username_from_email(email)
        if email == user_name:
            if any(word in email for word in domains_not_allowed):
                not_allowed_emails.append(email)
            else:
                not_found_emails.append(email)
        else:
            found_and_added_users.append(user_name)

    if found_and_added_users:
        for user in found_and_added_users:
            if not (CrowdBackend.find_existing_user(user)):
                CrowdBackend.create_user_from_crowd(user)
    return found_and_added_users, not_found_emails, not_allowed_emails


def get_crowd_config():
    """
    Returns CROWD-related project settings.
    """
    config = getattr(settings, 'CROWD', None)
    if not config:  # pragma: no cover
        raise UserWarning('CROWD configuration is not in your settings.py')
    return config
