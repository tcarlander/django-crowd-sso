from django.test import TestCase

from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
import logging


logger = logging.getLogger(__name__)


def mock_get_response(*args, **kwargs):
    global json_return
    url = args[0]
    status_code = 0
    # json_return = {}
    if 'search.json?entity-type=user&restriction=email' in url:
        status_code = 200
        if 'search.json?entity-type=user&restriction=email%3Dadmin@test.com' in url:
            json_return = {"expand": "user", "users": [{"link": {
                "href": "http://login.dev.wfptha.org/crowd/rest/usermanagement/1/user?username=tobias.carlander",
                "rel": "self"},
                "name": "admin"}]}
        else:
            json_return = {
                "expand": "user",
                "users": []
            }

    if 'config/cookie.json' in url:
        # cookie config
        status_code = 201
        json_return = {"domain": ".atlassian.com", "name": "crowd.token_key", "secure": False}
    if 'session/VALID_TOKEN.json' in url:
        # valid session for Admin
        status_code = 201
        json_return = {'user': {'name': 'admin'}}
    if 'session/None.json' in url:
        # Invalid session
        status_code = 400
        json_return = {"reason": "INVALID_SSO_TOKEN",
                       "message": "Failed to find entity of type [com.atlassian.crowd.model.token.Token]"}

    if 'session/INVLALID_TOKEN.json' in url:
        # Invalid session
        status_code = 400
        json_return = {"reason": "INVALID_SSO_TOKEN",
                       "message": "Failed to find entity of type [com.atlassian.crowd.model.token.Token]"}
    if 'user.json?username=admin' in url:
        # User Details of admin
        status_code = 201
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
                    "href":
                        "http://login.dev.wfptha.org/crowd/rest/usermanagement/latest/user/attribute?username=admin",
                    "rel": "self"
                }
            },
            "first-name": "Admin",
            "last-name": "Administrator",
            "display-name": "Admin Administrator",
            "email": "bordin.suetrong@wfp.org"
        }

    rg = Mock()
    rg.status_code = status_code
    rg.json.return_value = json_return
    return rg


def mock_local_user(username, password=''):
    global user
    User = get_user_model()

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
        self.assertEqual(response['location'], '/admin/login/?next=/admin/')

    def test_get_homepage_no_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_homepage_login_req(self):
        response = self.client.get('/l')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/login/?next=/l')
        r = Mock()
        r.status_code = 201
        r.json.return_value = {"token": "VALID_TOKEN"}
        mock_local_user('admin')
        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect = mock_get_response
        response = self.client.post('/admin/login/?next=/l', {'username': 'admin', 'password': '55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/l')

    def test_login_sucsessful_with_existing_crowd_user(self):
        r = Mock()
        r.status_code = 201
        r.json.return_value = {"token": "VALID_TOKEN"}
        mock_local_user('admin')
        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect = mock_get_response
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'admin', 'password': '55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)

    def test_login_sucsessful_with_existing_crowd_user_using_email(self):
        r = Mock()
        r.status_code = 201
        r.json.return_value = {"token": "VALID_TOKEN"}
        mock_local_user('admin')
        self.mock_requests_post.return_value = r
        self.mock_requests_get.side_effect = mock_get_response
        response = self.client.post('/admin/login/?next=/admin/',
                                    {'username': 'admin@test.com', 'password': '55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)

    def test_login_sucsessful_with_non_existing_crowd_user(self):
        self.mock_requests_get.side_effect = mock_get_response
        r = Mock()
        r.status_code = 201
        r.json.return_value = {"token": "VALID_TOKEN"}
        self.mock_requests_post.return_value = r
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'admin', 'password': '55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)

    def test_login_sucsessful_with_non_existing_crowd_user_using_email(self):
        self.mock_requests_get.side_effect = mock_get_response
        r = Mock()
        r.status_code = 201
        r.json.return_value = {"token": "VALID_TOKEN"}
        self.mock_requests_post.return_value = r
        response = self.client.post('/admin/login/?next=/admin/',
                                    {'username': 'admin@test.com', 'password': '55555555'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/admin/')
        response2 = self.client.get('/admin/')
        self.assertEqual(response2.status_code, 200)

    def test_sso_login_new_user(self):
        self.client.cookies['crowd.token_key'] = 'VALID_TOKEN'
        self.mock_requests_get.side_effect = mock_get_response
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_sso_login_existing_user(self):
        mock_local_user('admin')
        self.client.cookies['crowd.token_key'] = 'VALID_TOKEN'
        self.mock_requests_get.side_effect = mock_get_response
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_sso_logout(self):
        self.mock_requests_get.side_effect = mock_get_response
        self.client.cookies['crowd.token_key'] = 'VALID_TOKEN'
        self.client.session['CrowdToken'] = 'VALID_TOKEN'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.client.session['CrowdToken'] = 'VALID_TOKEN'
        self.client.cookies['crowd.token_key'] = ''
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_sso_logout_cookie_expiered(self):
        self.mock_requests_get.side_effect = mock_get_response
        self.client.cookies['crowd.token_key'] = 'VALID_TOKEN'
        self.client.get('/admin/')
        self.client.cookies['crowd.token_key'] = 'INVLALID_TOKEN'
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_sso_manual_logout(self):
        self.mock_requests_get.side_effect = mock_get_response
        self.client.cookies['crowd.token_key'] = 'VALID_TOKEN'
        r = Mock()
        r.status_code = 200
        r.json.return_value = {"token": "VALID_TOKEN"}
        self.mock_requests_delete.response = r
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.client.get('/admin/logout/')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_user_local_correct_login(self):
        mock_local_user('admin2')
        r = Mock()  # No Such crowd User
        r.status_code = 400
        self.mock_requests_get.side_effect = mock_get_response
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",
                               "message": "Account with name <admin3> failed to authenticate: User <admin3> does not "}
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'admin2', 'password': 'admin'})
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response['Location'], 'http://testserver/admin/')

    def test_user_local_correct_logout(self):
        self.mock_requests_get.side_effect = mock_get_response
        mock_local_user('admin2')
        r = Mock()  # No Such crowd User
        r.status_code = 400
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",
                               "message": "Account with name <admin3> failed to authenticate: User <admin3> does not "}
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'admin2', 'password': 'admin'})
        self.assertEqual(response.status_code, 200)
        self.client.get('/admin/logout/')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_user_not_exists(self):
        self.mock_requests_get.side_effect = mock_get_response
        r = Mock()  # No Such crowd User
        r.status_code = 400
        r.json.return_value = {"reason": "INVALID_USER_AUTHENTICATION",
                               "message": "Account with name <admin3> failed to authenticate: User <admin3> does not "}
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'admin2', 'password': 'admin'})
        my_response = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'Please enter the correct' in my_response)

    def test_import_list(self):
        from crowd.backends import import_users_from_email_list
        self.mock_requests_get.side_effect = mock_get_response
        r = Mock()
        r.status_code = 201
        r.json.return_value = {"token": "VALID_TOKEN"}
        self.mock_requests_post.return_value = r
        response = self.client.post('/admin/login/?next=/admin/',
                                    {'username': 'admin@test.com', 'password': '55555555'})
        emails = ["admin@test.com", "b@b.c", "c@b.c","abc@wfp.org"]
        added, not_added, blocked = import_users_from_email_list(emails)
        self.assertEquals(added, ['admin'])
        self.assertEquals(not_added, ['b@b.c', 'c@b.c'])
        self.assertEqual(blocked, ['abc@wfp.org'])
