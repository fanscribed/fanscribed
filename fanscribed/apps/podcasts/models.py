import datetime

from django.db import models

from django_extensions.db.models import CreationDateTimeField

from django_fsm.db.fields import FSMField, transition


class Podcast(models.Model):

    name = models.CharField(max_length=200, blank=True, null=True)
    rss_url = models.URLField(max_length=512)


class Episode(models.Model):

    podcast = models.ForeignKey(Podcast)
    title = models.URLField(max_length=200, blank=True, null=True)


class RssFetch(models.Model):

    podcast = models.ForeignKey(Podcast)
    created = CreationDateTimeField()
    fetched = models.DateField(blank=True, null=True)
    body = models.BinaryField(blank=True, null=True)
    state = FSMField(default='not-fetched', protected=True)

    @transition(state, 'not-fetched', 'fetched')
    def load_rss(self, body):
        self.body = body
        self.fetched = datetime.datetime.now()
