from django.test import TestCase
from unittest.mock import patch, Mock
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


def mock_get_response(*args,**kwargs):
            
            url = args[0]
            print(url)
            if url == 'http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/config/cookie.json':
                #cookie config
                status_code=201
                json_return = {   "domain" : ".atlassian.com",   "name" : "crowd.token_key",   "secure" : False}
            if url == 'http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/session/123456.json':
                #valid session for Admin
                status_code=201
                json_return = { 'user':{'name':'admin'}}
            if url == 'http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/session/123457.json':
                status_code=400
                #Invalid session
                json_return =  {
    "reason": "INVALID_SSO_TOKEN",
    "message": "Failed to find entity of type [com.atlassian.crowd.model.token.Token] with identifier [WXnUorKLQk3YIeThJRE7ig00]"}
    
            if url == 'http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/user.json?username=admin':
                # User Details of admin
                status_code=201
                json_return = {
                                "expand": "attributes",
                                "link": {
                                    "href": "http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/user?username=admin",
                                    "rel": "self"
                                },
                                "name": "admin",
                                "password": {
                                    "link": {
                                        "href": "http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/user/password?username=admin",
                                        "rel": "edit"
                                    }
                                },
                                "key": "32769:60f2a151-caeb-4471-966f-bbc57a5df714",
                                "active": True,
                                "attributes": {
                                    "attributes": [],
                                    "link": {
                                        "href": "http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/user/attribute?username=admin",
                                        "rel": "self"
                                    }
                                },
                                "first-name": "Admin",
                                "last-name": "Administrator",
                                "display-name": "Admin Administrator",
                                "email": "bordin.suetrong@wfp.org"
                            }

            rg=Mock()
            rg.status_code=status_code
            rg.json.return_value = json_return
            return rg

class TestLogin(TestCase):

    def setUp(self):
            patch_requests_post = patch('requests.post')
            self.mock_requests_post = patch_requests_post.start()
            self.addCleanup(patch_requests_post.stop)
            patch_requests_get = patch('requests.get')
            self.mock_requests_get = patch_requests_get.start()
            self.addCleanup(patch_requests_get.stop)
            
            
            
            
    def test_login_sucsessful_with_existing_crowd_user(self):
        print("test 1")
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "123456"}
        user = User.objects.create_user('admin', 'admin@test.com')
        user.set_unusable_password()
        user.first_name = 'Admin'
        user.last_name = 'Admin'
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()

        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect=mock_get_response
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin','password':'55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
    
    
    def test_login_sucsessful_with_non_existing_crowd_user(self):
        print("test 2")
        self.mock_requests_get.side_effect=mock_get_response        
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "123456"}        
        self.mock_requests_post.return_value = r 
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin','password':'55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
        
        
    def test_sso_login(self):
        print("\ntest test_sso_login")
        self.client.cookies['crowd.token_key']='123456'
        self.mock_requests_get.side_effect=mock_get_response        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        
    def test_sso_logout(self):
        print("\ntest test_sso_logout")
        self.mock_requests_get.side_effect=mock_get_response        
        self.client.cookies['crowd.token_key']='123456'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.client.cookies['crowd.token_key']=''
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        

    def test_sso_logout_cookie_expiered(self):
        print("\ntest test_sso_logout_cookie_expiered")
        self.mock_requests_get.side_effect=mock_get_response        
        self.client.cookies['crowd.token_key']='123456'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.client.cookies['crowd.token_key']='123457'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        

    def test_sso_manual_logout(self):
        print("\ntest test_sso_manual_logout")
        self.mock_requests_get.side_effect=mock_get_response        
        self.client.cookies['crowd.token_key']='123456'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/logout/')
        self.client.cookies['crowd.token_key']=response.cookies['crowd.token_key']
        print(response.cookies['crowd.token_key'])
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        
    
    def test_user_local_correct_login(self):
        user = User.objects.create_user('admin2', 'admin2@test.com')
        user.set_password('admin')
        user.first_name = 'Admin'
        user.last_name = 'Admin'
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
        r=Mock()# No Such crowd User
        r.status_code = 400
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",    "message": "Account with name <admin3> failed to authenticate: User <admin3> does not exist"}
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin2','password':'admin'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')

    def test_user_local_correct_logout(self):
        user = User.objects.create_user('admin2', 'admin2@test.com')
        user.set_password('admin')
        user.first_name = 'Admin'
        user.last_name = 'Admin'
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
        r=Mock()# No Such crowd User
        r.status_code = 400
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",    "message": "Account with name <admin3> failed to authenticate: User <admin3> does not exist"}
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin2','password':'admin'})

        response = self.client.get('/admin/logout/')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        
        
        
        
        
#    def test_user_not_exists(self):
#        self.assertTrue(True)