from decimal import Decimal

from django.conf import settings
from django.db import models

from model_utils.models import AutoCreatedField, TimeStampedModel

from django_fsm.db.fields import FSMField, transition

from .tasks import create_processed_transcript_media


# ---------------------


class SentenceFragment(models.Model):
    """A sentence fragment from within a transcript fragment."""

    revision = models.ForeignKey('TranscriptFragmentRevision')
    sequence = models.PositiveIntegerField()
    text = models.TextField()

    class Meta:
        unique_together = [
            ('revision', 'sequence'),
        ]


# ---------------------


class Task(TimeStampedModel):
    """A transcription task to be completed.

    state
    -----

    @startuml

    [*] --> unassigned
    unassigned --> assigned
    assigned --> presented
    presented --> submitted
    submitted --> processed
    processed --> [*]

    submitted --> invalid
    invalid --> presented

    assigned --> expired
    expired --> aborted
    presented --> aborted
    aborted --> [*]

    @enduml
    """

    class Meta:
        abstract = True

    transcript = models.ForeignKey('Transcript', related_name='tasks')
    state = FSMField(default='unassigned')
    is_review = models.BooleanField()


class TranscriptionTask(Task):

    revision = models.ForeignKey('TranscriptFragmentRevision')


# ---------------------


class Transcript(TimeStampedModel):
    """A transcript of audio or video to text.

    length_state
    ------------

    @startuml
    [*] --> unset
    unset --> set
    set --> [*]
    @enduml
    """

    name = models.CharField(max_length=512)  # TODO: change to `title`
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    length_state = FSMField(default='unset', protected=True)

    def __unicode__(self):
        return self.name

    def has_full_length_processed_media(self):
        return TranscriptMedia.objects.filter(
            transcript=self,
            is_processed=True,
            is_full_length=True,
        ).exists()

    @transition(length_state, 'unset', 'set', save=True)
    def set_length(self, length):
        self.length = length
        self._create_fragments()

    def _create_fragments(self):  # TODO: unit test
        start = Decimal('0')
        while start < self.length:

            # Find the end of the current fragment.
            # If remaining time is less than fragment length, stretch to end.
            end = start + settings.TRANSCRIPT_FRAGMENT_LENGTH
            remaining = self.length - end
            if remaining < settings.TRANSCRIPT_FRAGMENT_LENGTH:
                end = self.length

            self.fragments.create(
                start=start,
                end=end,
            )

            start = end


# ---------------------


class TranscriptFragmentManager(models.Manager):

    use_for_related_fields = True

    def empty(self):
        return self.filter(state='empty')

    def transcribed(self):
        return self.filter(state='transcribed')

    def reviewed(self):
        return self.filter(state='reviewed')

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
    transcribed --> reviewed
    reviewed --> [*]
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
    """A revision of a TranscriptFragment.

    state
    -----

    @startuml
    [*] --> editing
    editing --> changed
    editing --> not_changed
    editing --> cancelled
    changed --> [*]
    not_changed --> [*]
    cancelled --> [*]
    @enduml
    """

    fragment = models.ForeignKey('TranscriptFragment', related_name='revisions')
    revision = models.PositiveIntegerField()
    editor = models.ForeignKey('auth.User')
    created = AutoCreatedField()
    state = FSMField(default='editing')

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
    created = AutoCreatedField()
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
