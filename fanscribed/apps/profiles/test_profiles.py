from random import randint

from django.contrib.auth.models import User
from django.test import TestCase


class NicknameTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test{}'.format(randint(1000, 9999)))

    def test_default_profile_has_no_nickname(self):
        self.assertIsNone(self.user.profile.nickname)
