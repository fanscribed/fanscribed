from django.db import models

from django_extensions.db.models import CreationDateTimeField

from django_fsm.db.fields import FSMField


class Transcript(models.Model):

    created = CreationDateTimeField()
    name = models.CharField(max_length=512)
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    length_state = FSMField(default='unknown', protected=True)

    def __unicode__(self):
        return self.name


class TranscriptMedia(models.Model):

    transcript = models.ForeignKey('Transcript')
    media_file = models.ForeignKey('media.MediaFile')
    is_raw_media = models.BooleanField(help_text='Is it unprocessed media?')
    is_full_length = models.BooleanField(
        help_text='Is it the full length of media to be transcribed?')
    created = CreationDateTimeField()
    start = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    end = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    timecode_state = FSMField(default='unknown', protected=True)

    class Meta:
        unique_together = (
            'transcript',
            'is_raw_media',
            'is_full_length',
            'start',
            'end',
        )

    def __unicode__(self):
        if self.is_raw_media:
            return u'Raw media for {self.transcript}'.format(**locals())
        else:
            return u'Generated media for {self.transcript}'.format(**locals())
