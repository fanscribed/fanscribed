from random import randint

from django.contrib.auth.models import User
from django.test import TestCase

from django_fsm.db.fields.fsmfield import TransitionNotAllowed


class NicknameTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test{}'.format(randint(1000, 9999)))
        self.user2 = User.objects.create(
            username='test{}'.format(randint(10000, 99999)))
        self.profile = self.user.profile
        self.profile2 = self.user2.profile

    def test_default_profile_has_no_nickname(self):
        self.assertIsNone(self.user.profile.nickname)

    def test_can_change_nickname(self):
        self.profile.set_nickname(u'my nickname')

    def test_can_change_nickname_only_once(self):
        self.profile.set_nickname(u'my nickname')
        self.profile.save()

        self.assertRaises(
            TransitionNotAllowed,
            self.profile.set_nickname, u'my second nickname',
        )

    def test_cannot_change_nickname_slug_already_in_use(self):
        self.profile.set_nickname(u'my nickname')
        self.profile.save()

        self.assertRaises(
            ValueError,
            self.profile2.set_nickname, u'My NickName',
        )

    def test_nickname_cannot_be_empty(self):
        self.assertRaises(
            ValueError,
            self.profile.set_nickname, u'',
        )

    def test_nickname_whitespace_normalized(self):
        self.profile.set_nickname(u'   My   New  \n  Nickname   ')
        self.assertEqual(self.profile.nickname, u'My New Nickname')
        self.assertEqual(self.profile.nickname_slug, u'my-new-nickname')
