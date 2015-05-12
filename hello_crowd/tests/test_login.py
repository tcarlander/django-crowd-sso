from django.test import TestCase
try:
    from unittest.mock import patch, Mock
except:
    from mock import patch, Mock
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


def mock_get_response(*args,**kwargs):
            
            url = args[0]
            print(url)
            status_code =0
            #json_return = {}
            if 'search.json?entity-type=user&restriction=email' in url:
                print('email check')
                status_code = 200
                if 'search.json?entity-type=user&restriction=email%3Dadmin@test.com'in url:
                    print("Hit")
                    json_return = {"expand": "user","users": [{"link": {"href": "http://login.dev.wfptha.org/crowd/rest/usermanagement/1/user?username=tobias.carlander","rel": "self"},
                                            "name": "admin"}]}
                else:
                    print("Miss")
                    json_return = {
                                        "expand": "user",
                                        "users": []
                                    }

            if 'config/cookie.json' in url:
                #cookie config
                status_code=201
                json_return = {   "domain" : ".atlassian.com",   "name" : "crowd.token_key",   "secure" : False}
            if 'session/VALID_TOKEN.json' in url:
                #valid session for Admin
                status_code=201
                json_return = { 'user':{'name':'admin'}}
            if 'session/None.json'  in url:
                #Invalid session
                status_code=400
                json_return =  {"reason": "INVALID_SSO_TOKEN","message": "Failed to find entity of type [com.atlassian.crowd.model.token.Token] with identifier [WXnUorKLQk3YIeThJRE7ig00]"}

            if 'session/INVLALID_TOKEN.json'  in url:
                #Invalid session
                status_code=400
                json_return =  {"reason": "INVALID_SSO_TOKEN","message": "Failed to find entity of type [com.atlassian.crowd.model.token.Token] with identifier [WXnUorKLQk3YIeThJRE7ig00]"}
            if 'user.json?username=admin'  in url:
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

def mock_local_user(username,password=''):
    if username == 'admin':
        user = User.objects.create_user('admin', 'admin@test.com')
        user.set_unusable_password()
        user.first_name = 'Admin'
        user.last_name = 'Admin'
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
    if username == 'admin2':
        user = User.objects.create_user('admin2', 'admin2@test.com')
        user.set_password('admin')
        user.first_name = 'Admin'
        user.last_name = 'Admin'
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
    return user

class TestLogin(TestCase):

    def setUp(self):
        patch_requests_post = patch('requests.post')
        self.mock_requests_post = patch_requests_post.start()
        self.addCleanup(patch_requests_post.stop)
        patch_requests_get = patch('requests.get')
        self.mock_requests_get = patch_requests_get.start()
        self.addCleanup(patch_requests_get.stop)
        patch_requests_delete = patch('requests.delete')
        self.mock_requests_delete = patch_requests_delete.start()
        self.addCleanup(patch_requests_delete.stop)
            
            
            
    def test_not_logged_in(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'],'http://testserver/admin/login/?next=/admin/')

    def test_get_homepage_not_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def OFF_test_get_homepage_not_login_req(self):
        response1 = self.client.get('/l')
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response1['location'],'http://testserver/admin/login/?next=/l')
        logger.debug("test 1")
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "VALID_TOKEN"}
        user = mock_local_user('admin')
        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect=mock_get_response
        response3 = self.client.post('/admin/login/?next=/l',{'username':'admin','password':'55555555'})
        self.assertEqual(response3.status_code, 302)
        self.assertEqual(response3['Location'],'http://testserver/l')
        response2 = self.client.get('/l')
        self.assertEqual(response2.status_code, 200)



    def test_login_sucsessful_with_existing_crowd_user(self):
        logger.debug("test 1")
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "VALID_TOKEN"}
        user = mock_local_user('admin')
        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect=mock_get_response
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin','password':'55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)


    def test_login_sucsessful_with_existing_crowd_user_using_email(self):
        logger.debug("Email Login")
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "VALID_TOKEN"}
        user = mock_local_user('admin')
        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect=mock_get_response
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin@test.com','password':'55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)

    
    
    def test_login_sucsessful_with_non_existing_crowd_user(self):
        logger.debug("test 2")
        self.mock_requests_get.side_effect=mock_get_response        
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "VALID_TOKEN"}        
        self.mock_requests_post.return_value = r 
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin','password':'55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)

    def test_login_sucsessful_with_non_existing_crowd_user_using_email(self):
        logger.debug("test 2 email")
        self.mock_requests_get.side_effect=mock_get_response        
        r=Mock()
        r.status_code = 201
        r.json.return_value = {   "token" : "VALID_TOKEN"}        
        self.mock_requests_post.return_value = r 
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin@test.com','password':'55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)
        
    def test_sso_login_new_user(self):
        logger.debug("\ntest test_sso_login")
        self.client.cookies['crowd.token_key']='VALID_TOKEN'
        self.mock_requests_get.side_effect=mock_get_response        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_sso_login_existing_user(self):
        logger.debug("\ntest test_sso_login_existing_user")
        user = mock_local_user('admin')
        self.client.cookies['crowd.token_key']='VALID_TOKEN'
        self.mock_requests_get.side_effect=mock_get_response        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        
    def test_sso_logout(self):
        logger.debug("\ntest test_sso_logout")
        self.mock_requests_get.side_effect=mock_get_response        
        self.client.cookies['crowd.token_key']='VALID_TOKEN'
        self.client.session['CrowdToken']='VALID_TOKEN'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.client.session['CrowdToken']='VALID_TOKEN'
        self.client.cookies['crowd.token_key']=''
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        

    def test_sso_logout_cookie_expiered(self):
        logger.debug("\ntest test_sso_logout_cookie_expiered")
        self.mock_requests_get.side_effect=mock_get_response        
        self.client.cookies['crowd.token_key']='VALID_TOKEN'
        response = self.client.get('/admin/')
        self.client.cookies['crowd.token_key']='INVLALID_TOKEN'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        


    def test_sso_manual_logout(self):
        logger.debug("\ntest test_sso_manual_logout")
        self.mock_requests_get.side_effect=mock_get_response        
        self.client.cookies['crowd.token_key']='VALID_TOKEN'
        r=Mock()
        r.status_code = 200
        r.json.return_value = {   "token" : "VALID_TOKEN"}
        self.mock_requests_delete.response = r
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/logout/')
        #self.client.cookies['crowd.token_key'].value=response.cookies['crowd.token_key'].value
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        
    
    def test_user_local_correct_login(self):
        logger.debug("\ntest test_user_local_correct_login")
        user = mock_local_user('admin2')
        r=Mock()# No Such crowd User
        r.status_code = 400
        self.mock_requests_get.side_effect=mock_get_response   
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",    "message": "Account with name <admin3> failed to authenticate: User <admin3> does not exist"}
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin2','password':'admin'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')

    def test_user_local_correct_logout(self):
        self.mock_requests_get.side_effect=mock_get_response   
        user = mock_local_user('admin2')
        r=Mock()# No Such crowd User
        r.status_code = 400
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",    "message": "Account with name <admin3> failed to authenticate: User <admin3> does not exist"}
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin2','password':'admin'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],'http://testserver/admin/')
        response = self.client.get('/admin/logout/')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)        
        
    def test_user_not_exists(self):
        self.mock_requests_get.side_effect=mock_get_response   
        r=Mock()# No Such crowd User
        r.status_code = 400
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",    "message": "Account with name <admin3> failed to authenticate: User <admin3> does not exist"}
        response = self.client.post('/admin/login/?next=/admin/',{'username':'admin2','password':'admin'})
        my_response = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.' in my_response)
