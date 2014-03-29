from django.db import models

from django_extensions.db.models import CreationDateTimeField

from django_fsm.db.fields import FSMField

from .tasks import create_processed_transcript_media


# ---------------------


class Transcript(models.Model):

    created = CreationDateTimeField()
    name = models.CharField(max_length=512)  # TODO: change to `title`
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __unicode__(self):
        return self.name

    def has_full_length_processed_media(self):
        return TranscriptMedia.objects.filter(
            transcript=self,
            is_processed=True,
            is_full_length=True,
        ).exists()


# ---------------------


class TranscriptFragmentManager(models.Manager):

    use_for_related_fields = True

    def empty(self):
        return self.filter(state='empty')

    def transcribed(self):
        return self.filter(state='transcribed')

    def locked(self):
        return self.filter(locked_state='locked')

    def unlocked(self):
        return self.filter(locked_state='unlocked')


class TranscriptFragment(models.Model):
    """A fragment of a transcript defined by its time span.

    state
    -----

    @startuml
    [*] --> empty
    empty --> transcribed
    @enduml

    locked_state
    ------------

    @startuml
    [*] --> unlocked
    unlocked --> locked
    locked --> unlocked
    @enduml
    """

    transcript = models.ForeignKey('Transcript', related_name='fragments')
    start = models.DecimalField(max_digits=8, decimal_places=2)
    end = models.DecimalField(max_digits=8, decimal_places=2)
    state = FSMField(default='empty')
    locked_by = models.ForeignKey('auth.User', blank=True, null=True)
    locked_at = models.DateTimeField(blank=True, null=True)
    locked_state = FSMField(default='unlocked')

    objects = TranscriptFragmentManager()

    class Meta:
        unique_together = [
            ('transcript', 'start', 'end'),
        ]


# ---------------------


class TranscriptFragmentRevision(models.Model):

    fragment = models.ForeignKey('TranscriptFragment', related_name='revisions')
    revision = models.PositiveIntegerField()
    editor = models.ForeignKey('auth.User')
    created = CreationDateTimeField()
    changed = models.BooleanField(
        help_text='True if first revision, or changed since last revision.')

    class Meta:
        unique_together = [
            ('fragment', 'revision'),
        ]


# ---------------------


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
