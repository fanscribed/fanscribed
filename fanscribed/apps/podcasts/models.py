import datetime

from django.db import models
from django.dispatch import receiver

from django_extensions.db.models import CreationDateTimeField

from django_fsm.signals import post_transition
from django_fsm.db.fields import FSMField, transition

import feedparser


class Podcast(models.Model):
    """A podcast we want to have in our directory.

    approval_state
    --------------

    @startuml
    [*] --> not_approved
    not_approved --> owner_verified
    not_approved --> user_approved
    not_approved --> staff_approved
    user_approved --> staff_approved
    user_approved --> owner_verified
    staff_approved --> owner_verified
    @enduml
    """

    rss_url = models.URLField(max_length=512, unique=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    approval_state = FSMField(default='not_approved', protected=True)

    # approval_state
    # --------------

    @transition(approval_state,
                source='not_approved',
                target='user_approved',
                save=True)
    def user_approve(self, user, notes=None):
        TranscriptionApproval.objects.create(
            podcast=self,
            user=user,
            approval_type='user',
            notes=notes,
        )

    @transition(approval_state,
                source=['not_approved', 'user_approved'],
                target='staff_approved',
                save=True)
    def staff_approve(self, user, notes=None):
        TranscriptionApproval.objects.create(
            podcast=self,
            user=user,
            approval_type='staff',
            notes=notes,
        )

    @transition(approval_state,
                source=['not_approved', 'user_approved', 'staff_approved'],
                target='owner_verified',
                save=True)
    def owner_verify(self, user, notes=None):
        TranscriptionApproval.objects.create(
            podcast=self,
            user=user,
            approval_type='owner',
            notes=notes,
        )


APPROVAL_TYPE_CHOICES = [
    ('user', 'User'),
    ('staff', 'Staff'),
    ('owner', 'Onwer'),
]

class TranscriptionApproval(models.Model):
    """
    A record of a user indicating we are allowed to transcribe the podcast.
    """

    podcast = models.ForeignKey('Podcast')
    user = models.ForeignKey('auth.User')
    approval_type = models.CharField(max_length=5, choices=APPROVAL_TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)


class RssFetch(models.Model):
    """A fetch of the RSS feed of a podcast.

    @startuml
    [*] --> not_fetched
    not_fetched --> fetching
    fetching --> fetched
    fetching --> failed
    not_fetched --> fetched
    fetched --> [*]
    failed --> [*]
    @enduml
    """

    podcast = models.ForeignKey(Podcast)
    created = CreationDateTimeField()
    fetched = models.DateField(blank=True, null=True)
    body = models.BinaryField(blank=True, null=True)
    state = FSMField(default='not_fetched', protected=True)

    @transition(state, 'not_fetched', 'fetched')
    def load_rss(self, body):
        self.body = body
        self.fetched = datetime.datetime.now()

    @transition(state, 'not_fethed', 'fetching')
    def start(self):
        self.fetched = datetime.datetime.now()

    @transition(state, 'fetching', 'fetched')
    def finish(self, body):
        self.body = body

    @transition(state, 'fetching', 'failed')
    def fail(self):
        pass


@receiver(post_transition, sender=RssFetch)
def update_podcast_title_from_rssfetch(sender, instance, target, **kwargs):
    """
    :type instance: RssFetch
    """
    if target == 'fetched':
        d = feedparser.parse(instance.body)
        podcast = instance.podcast
        podcast.title = d['feed']['title']
        podcast.save()
