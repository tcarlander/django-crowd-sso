# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase
import simplejson
from user.models import AuthUser


class AuthenticationTest(TestCase):
    def setUp(self):
        self.user = AuthUser.objects.create_user(email='testuser@proteus-tech.com', username='testuser', password='secret')
        self.data = {
            'email': 'testuser@proteus-tech.com',
            'password': 'secret'
        }

    def test_login(self):
        uri = reverse('login')
        json_data = simplejson.dumps(self.data)
        response = self.client.post(uri, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login_with_invalid_user(self):
        uri = reverse('login')
        invalid_user_data = {
            'email': 'victoria@proteus-tech.com',
            'password': 'secret'
        }
        json_data = simplejson.dumps(invalid_user_data)
        response = self.client.post(uri, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_with_inactive_user(self):
        uri = reverse('login')
        inactive_user = AuthUser.objects.create_user(email='inactiveuser@proteus-tech.com', username='inactiveuser', password='secret')
        inactive_user.is_active = False
        inactive_user.save()
        inactive_user_data = {
            'email': 'inactiveuser@proteus-tech.com',
            'password': 'secret'
        }

        json_data = simplejson.dumps(inactive_user_data)
        response = self.client.post(uri, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        self.client.login(email=self.user.email, password='secret')
        uri = reverse('logout')
        response = self.client.post(uri)
        self.assertEqual(response.status_code, 200)
