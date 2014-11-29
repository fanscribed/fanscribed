"""Podcast registration tests."""

from httplib import OK

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class RegistrationTestCase(TestCase):

    def setUp(self):
        self.account_login_url = reverse('account_login')
        self.register_url = reverse('podcasts:register')

    def test_registration_requires_login(self):
        # Without login.
        response = self.client.get(self.register_url)
        expected_url = self.account_login_url + '?next=' + self.register_url
        self.assertRedirects(response, expected_url)

        # With login.
        user = User.objects.create_user(
            'user', 'user@example.com', 'password',
            first_name='Regular', last_name='User')
        self.client.login(username='user', password='password')
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, OK)
