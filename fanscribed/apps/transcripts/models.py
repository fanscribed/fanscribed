from django.db import models

from django_extensions.db.models import CreationDateTimeField

from .tasks import create_processed_transcript_media


class Transcript(models.Model):

    created = CreationDateTimeField()
    name = models.CharField(max_length=512)
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __unicode__(self):
        return self.name

    def has_full_length_processed_media(self):
        return TranscriptMedia.objects.filter(
            transcript=self,
            is_processed=True,
            is_full_length=True,
        ).exists()


class TranscriptMedia(models.Model):

    # TODO: state machine around conversion process

    transcript = models.ForeignKey('Transcript')
    media_file = models.ForeignKey('media.MediaFile')
    is_processed = models.BooleanField(help_text='Is it processed media?')
    is_full_length = models.BooleanField(
        help_text='Is it the full length of media to be transcribed?')
    created = CreationDateTimeField()
    start = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    end = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    class Meta:
        unique_together = (
            'transcript',
            'is_processed',
            'is_full_length',
            'start',
            'end',
        )

    def __unicode__(self):
        if self.is_processed:
            return u'Processed media for {self.transcript}'.format(**locals())
        else:
            return u'Raw media for {self.transcript}'.format(**locals())

    def create_processed(self):
        create_processed_transcript_media.delay(self.pk)
