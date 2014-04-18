import datetime
import time

from django.db import models
from django.dispatch import receiver
from django.utils.timezone import utc
from django_extensions.db.models import CreationDateTimeField
from django_fsm.signals import post_transition
from django_fsm.db.fields import FSMField, transition
import feedparser

from . import tasks


# ------------------------------------------------------------------------------


class Episode(models.Model):
    """An episode of a podcast."""

    podcast = models.ForeignKey('Podcast', related_name='episodes')
    guid = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    published = models.DateTimeField()
    media_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    transcript = models.OneToOneField('transcripts.Transcript', blank=True, null=True,
                                      related_name='episode')

    class Meta:
        ordering = ('-published',)
        unique_together = [
            ('podcast', 'guid'),
        ]

    def __unicode__(self):
        return u'self.title ({self.podcast})'.format(**locals())


# ------------------------------------------------------------------------------


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

    rss_url = models.URLField(unique=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    approval_state = FSMField(default='not_approved', protected=True)

    def __unicode__(self):
        return self.title or self.rss_url

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


# ------------------------------------------------------------------------------


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

    podcast = models.ForeignKey(Podcast, related_name='fetches')
    created = CreationDateTimeField()
    fetched = models.DateTimeField(blank=True, null=True)
    body = models.BinaryField(blank=True, null=True)
    state = FSMField(default='not_fetched', protected=True)

    @transition(state, 'not_fetched', 'fetched', save=True)
    def load_rss(self, body=None, filename=None):
        if body is not None:
            self.body = body
        elif filename is not None:
            with open(filename, 'rb') as f:
                self.body = f.read()
        else:
            raise TypeError('Specify either `body` or `filename`.')
        self.fetched = datetime.datetime.now()

    @transition(state, 'not_fetched', 'fetching', save=True)
    def start(self):
        self.fetched = datetime.datetime.now()

    @transition(state, 'fetching', 'fetched', save=True)
    def finish(self, body):
        self.body = body

    @transition(state, 'fetching', 'failed', save=True)
    def fail(self):
        pass


@receiver(post_transition, sender=RssFetch)
def fetch_when_rssfetch_started(instance, target, **kwargs):
    """
    :type instance: RssFetch
    """
    if target == 'fetching':
        tasks.fetch_rss.delay(instance.pk)


def datetime_from_feedparser(entry):
    return datetime.datetime.fromtimestamp(
        time.mktime(entry.published_parsed), tz=utc)


@receiver(post_transition, sender=RssFetch)
def update_podcast_title_and_episodes_from_rssfetch(instance, target, **kwargs):
    """
    :type instance: RssFetch
    """
    if target == 'fetched':
        d = feedparser.parse(instance.body)

        podcast = instance.podcast
        podcast.title = d['feed']['title']
        podcast.save()

        for entry in d.entries:
            if 'id' not in entry or entry.published_parsed is None:
                continue
            existing_episode = Episode.objects.filter(
                podcast=podcast, guid=entry.id)
            if not existing_episode.exists():
                published = datetime_from_feedparser(entry)
                media_url = entry.enclosures[0]['href']
                Episode.objects.create(
                    podcast=podcast,
                    guid=entry.id,
                    title=entry.title,
                    published=published,
                    media_url=media_url,
                    description=entry.description,
                )


# ------------------------------------------------------------------------------


class TranscriptionApproval(models.Model):
    """
    A record of a user indicating we are allowed to transcribe the podcast.
    """

    APPROVAL_TYPE_CHOICES = [
        ('user', 'User'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
    ]

    podcast = models.ForeignKey('Podcast')
    created = CreationDateTimeField()
    user = models.ForeignKey('auth.User', blank=True, null=True)
    approval_type = models.CharField(max_length=5, choices=APPROVAL_TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)
