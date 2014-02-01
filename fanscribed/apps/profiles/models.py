"""User profile models.

Inspired by http://www.turnkeylinux.org/blog/django-profile
"""

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):

    user = models.ForeignKey(User, unique=True)


# Add a property to User to always get-or-create a corresponding Profile.
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
