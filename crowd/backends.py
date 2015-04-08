from django.contrib.auth.models import User
from django.conf import settings
from xml.dom.minidom import parseString
from django.contrib.auth.backends import ModelBackend
import requests, json


class CrowdBackend(ModelBackend):
    """
    This is the Attlasian CROWD (JIRA) Authentication Backend for Django
    Have a nice day! Hope you will never need opening this file looking for a bug =)
    """
    def authenticate(self, username, password):
        """
        Main authentication method
        """
        crowd_config = self._get_crowd_config()
        if not crowd_config:
            return None
#        try:
        user = self._find_existing_user(username)
        resp, content = self._call_crowd_session(username, password, crowd_config)
        if resp == 201:
            if not user:
                user = self._create_new_user_from_crowd_response(username, crowd_config)
            return user
        else:
            return None
 #       except:
 #           return None
            


    def _get_crowd_config(self):
        """
        Returns CROWD-related project settings. Private service method.
        """
        config = getattr(settings, 'CROWD', None)
        if not config:
            raise UserWarning('CROWD configuration is not set in your settings.py, while authorization backend is set')
        return config

    def _find_existing_user(self, username):
        """
        Finds an existing user with provided username if one exists. Private service method.
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
        json_object = {'username' : username ,'password' : password ,'validation-factors' : {'validationFactors' : [{'name' : 'remote_address','value' : '127.0.0.1'}]}}
        print( json_object)
        r = requests.post(url, auth=(crowd_config['app_name'], crowd_config['password']),data=json.dumps(json_object),headers={'content-type': 'application/json','Accept': 'application/json'})
        resp = r.status_code
        print (resp)
        print(r.json())
        return resp, None # sorry for this verbosity, but it gives a better understanding


    def _create_new_user_from_crowd_response(self, username, crowd_config):
        """
        Creating a new user in django auth database basing on information provided by CROWD. Private service method.
        """
        
        url = crowd_config['url'] + ('/usermanagement/latest/user.json?username=%s' % (username,))
        r = requests.get(url, auth=(crowd_config['app_name'], crowd_config['password']))
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
