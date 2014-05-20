"""User profile models.

Inspired by http://www.turnkeylinux.org/blog/django-profile
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from django_fsm.db.fields import FSMField, transition


TASK_ORDER_CHOICES = [
    ('eager', 'Give me different kinds of tasks when they are available.'),
    ('sequential', 'Give me the same kinds of tasks in sequence.'),
]


class Profile(models.Model):

    user = models.ForeignKey(User, unique=True)

    nickname = models.CharField(max_length=100, blank=True, null=True)
    nickname_slug = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    nickname_state = FSMField(default='unset', protected=True)

    task_types = models.ManyToManyField(
        'TaskType',
        verbose_name='Which tasks would you like to help with?')
    wants_reviews = models.BooleanField(
        verbose_name="Help review other's tasks.",
        help_text="Reviewing other's tasks helps finish transcripts faster.",
        default=False)
    task_order = models.CharField(
        choices=TASK_ORDER_CHOICES,
        verbose_name='Which order would you like to receive tasks?',
        default='eager',
        max_length=10)

    def __unicode__(self):
        if self.nickname:
            fmt = '{self.nickname} ({self.user.username})'
        else:
            fmt = '{self.user.username}'
        return fmt.format(**locals())

    def get_absolute_url(self):
        pk = self.user.pk  # Line up URL with User pk, not Profile.
        return reverse('profiles:detail', kwargs=dict(pk=pk))

    @property
    def preferred_task_names(self):
        return set(v['name'] for v in self.task_types.values('name'))

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


class TaskType(models.Model):

    # See 0004_load_default_data for the data migration that populates this.

    name = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0, unique=True)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return u'{}: {}'.format(self.name.title(), self.description)


# New users start out preferring all task types.
@receiver(models.signals.post_save, sender=Profile)
def new_profiles_prefer_all_task_types(instance, created, raw, **kwargs):
    if created and not raw:
        instance.task_types.add(*TaskType.objects.all())


# Add a property to User to always get-or-create a corresponding Profile.
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
