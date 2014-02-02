"""User profile models.

Inspired by http://www.turnkeylinux.org/blog/django-profile
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from django_fsm.db.fields import FSMField, transition


class Profile(models.Model):

    user = models.ForeignKey(User, unique=True)

    nickname = models.CharField(max_length=100, blank=True, null=True)
    nickname_slug = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    nickname_state = FSMField(default='unset', protected=True)

    @transition(nickname_state, 'unset', 'set')
    def set_nickname(self, new_nickname):
        new_nickname = u' '.join(new_nickname.strip().split())
        if new_nickname == u'':
            raise ValueError('Nickname cannot be empty')
        new_slug = slugify(new_nickname)
        if Profile.objects.filter(nickname_slug=new_slug).exclude(pk=self.pk):
            raise ValueError('Nickname already in use by another user')
        else:
            self.nickname = new_nickname
            self.nickname_slug = new_slug


    # Add a property to User to always get-or-create a corresponding Profile.
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
