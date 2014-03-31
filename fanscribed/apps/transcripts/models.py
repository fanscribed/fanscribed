from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from model_utils.models import AutoCreatedField, TimeStampedModel

from django_fsm.db.fields import FSMField, transition

from .tasks import create_processed_transcript_media


# ---------------------


class SentenceManager(models.Manager):

    use_for_related_fields = True

    def empty(self):
        return self.filter(state='empty')

    def partial(self):
        return self.filter(state='partial')

    def completed(self):
        return self.filter(state='completed')


class Sentence(models.Model):
    """A sentence made from sentence fragments.

    @startuml
    [*] --> empty
    empty --> partial
    partial --> completed
    @enduml
    """

    transcript = models.ForeignKey('Transcript', related_name='sentences')
    state = FSMField(default='empty', protected=True)
    fragments = models.ManyToManyField(
        'SentenceFragment', related_name='sentences')
    fragment_candidates = models.ManyToManyField(
        'SentenceFragment', related_name='candidate_sentences')
    tf_start = models.ForeignKey('TranscriptFragment')
    tf_sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ('tf_start__start', 'tf_sequence')

    objects = SentenceManager()

    @property
    def text(self):
        return u' '.join(fragment.text for fragment in self.fragments.all())

    @transition(state, ['empty', 'partial'], 'partial', save=True)
    def add_candidates(self, *fragments):
        self.fragment_candidates.add(*fragments)

    @transition(state, 'partial', 'partial', save=True)
    def remove_candidates(self, *fragments):
        self.fragment_candidates.remove(*fragments)

    @transition(state, 'partial', 'partial', save=True)
    def commit_candidates(self, *candidates):
        self.fragments.add(*candidates)
        self.fragment_candidates.remove(*candidates)

    @transition(state, 'partial', 'completed', save=True)
    def complete(self):
        pass


# ---------------------


class SentenceFragment(models.Model):
    """A sentence fragment from within a transcript fragment."""

    revision = models.ForeignKey('TranscriptFragmentRevision',
                                 related_name='sentence_fragments')
    sequence = models.PositiveIntegerField()
    text = models.TextField()

    class Meta:
        ordering = ('revision__fragment__start', 'sequence')
        unique_together = [
            ('revision', 'sequence'),
        ]


# ---------------------


class TaskManager(models.Manager):

    use_for_related_fields = True

    def presented(self):
        return self.filter(state='presented')

    def valid(self):
        return self.filter(state='valid')

    def invalid(self):
        return self.filter(state='invalid')


class Task(TimeStampedModel):
    """A transcription task to be completed.

    state
    -----

    @startuml

    [*] --> unassigned
    unassigned --> assigned
    assigned --> presented
    presented --> submitted
    submitted --> valid
    valid --> [*]

    submitted --> invalid
    invalid --> presented

    assigned --> expired
    expired --> aborted
    presented --> aborted
    aborted --> [*]

    @enduml
    """

    transcript = models.ForeignKey('Transcript')
    is_review = models.BooleanField()
    state = FSMField(default='unassigned', protected=True)
    assignee = models.ForeignKey('auth.User', blank=True, null=True)

    class Meta:
        abstract = True

    objects = TaskManager()

    def get_absolute_url(self):
        return reverse('transcripts:task_perform', kwargs=dict(
            transcript_pk=self.transcript.pk,
            type=self.TASK_TYPE,
            pk=self.pk,
        ))

    @transition(state, 'unassigned', 'assigned', save=True)
    def assign_to(self, user):
        self.assignee = user
        self._assign_to()

    def _assign_to(self):
        raise NotImplementedError()

    @transition(state, 'assigned', 'presented', save=True)
    def present(self):
        pass

    @transition(state, 'presented', 'submitted', save=True)
    def submit(self):
        self._submit()
        if not settings.TESTING:
            self._post_submit(self)

    def _submit(self):
        raise NotImplementedError()

    def _post_submit(self):
        raise NotImplementedError()

    @transition(state, 'submitted', 'valid', save=True)
    def validate(self):
        self._validate()

    def _validate(self):
        raise NotImplementedError()

    @transition(state, 'submitted', 'invalid', save=True)
    def invalidate(self):
        self._invalidate()

    def _invalidate(self):
        raise NotImplementedError()


class TranscribeTask(Task):

    TASK_TYPE = 'transcribe'

    revision = models.ForeignKey('TranscriptFragmentRevision',
                                 blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    # Keep start and end even if `revision` goes away.
    start = models.DecimalField(max_digits=8, decimal_places=2)
    end = models.DecimalField(max_digits=8, decimal_places=2)

    def _assign_to(self):
        self.revision.fragment.lock()

    def _submit(self):
        pass

    def _post_submit(self):
        from .tasks import process_transcribe_task
        result = process_transcribe_task.delay(self.pk)

    def _validate(self):
        self.revision.fragment.unlock()

    def _invalidate(self):
        fragment = self.revision.fragment
        self.revision.delete()
        self.revision = None
        fragment.unlock()


class StitchTask(Task):

    TASK_TYPE = 'stitch'

    left = models.ForeignKey('TranscriptFragmentRevision', related_name='+')
    right = models.ForeignKey('TranscriptFragmentRevision', related_name='+')

    def _assign_to(self):
        self.left.fragment.lock()
        self.right.fragment.lock()

    def _submit(self):
        pass

    def _post_submit(self):
        from .tasks import process_stitch_task
        process_stitch_task.delay(self.pk)

    def _validate(self):
        self.left.fragment.unlock()
        self.right.fragment.unlock()

    def _invalidate(self):
        self.left.fragment.unlock()
        self.right.fragment.unlock()

    def create_pairings_from_existing_candidates(self):
        # Create StitchTaskPairings based on existing candidate pairings.
        for left_fragment in self.left.sentence_fragments.all():
            for left_sentence in left_fragment.candidate_sentences.all():
                left_sentence_fragment = None
                right_sentence_fragment = None
                for candidate in left_sentence.fragment_candidates.all():
                    if candidate.revision == self.left:
                        left_sentence_fragment = candidate
                    if candidate.revision == self.right:
                        right_sentence_fragment = candidate
                if (left_sentence_fragment is not None
                    and right_sentence_fragment is not None
                ):
                    self.task_pairings.create(
                        left=left_sentence_fragment,
                        right=right_sentence_fragment,
                    )


class StitchTaskPairing(models.Model):

    task = models.ForeignKey('StitchTask', related_name='task_pairings')
    left = models.ForeignKey('SentenceFragment', related_name='+')
    right = models.ForeignKey('SentenceFragment', related_name='+')

    class Meta:
        ordering = ('left__revision__fragment__start', 'left__sequence')
        unique_together = [
            ('task', 'left',),
        ]


# Mapping of task types to model classes
TASK_MODEL = {
    # task_type: model_class,
    'transcribe': TranscribeTask,
    'stitch': StitchTask,
}


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
        self.length = Decimal(length)
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
                # First and last fragments are 'stitched' to each end. :)
                stitched_left=True if start == Decimal('0') else False,
                stitched_right=True if end == self.length else False,
            )

            start = end


# ---------------------


class TranscriptFragmentManager(models.Manager):

    use_for_related_fields = True

    def empty(self):
        return self.filter(state='empty')

    def transcribed(self):
        return self.filter(state='transcribed')

    def transcript_reviewed(self):
        return self.filter(state='transcript_reviewed')

    def stitched(self):
        return self.filter(state='stitched')

    def stitch_reviewed(self):
        return self.filter(state='stitch_reviewed')

    def locked(self):
        return self.filter(lock_state='locked')

    def unlocked(self):
        return self.filter(lock_state='unlocked')


class TranscriptFragment(models.Model):
    """A fragment of a transcript defined by its time span.

    state
    -----

    @startuml
    [*] --> empty
    empty --> transcribed
    transcribed --> transcript_reviewed
    transcript_reviewed --> stitched
    stitched --> stitch_reviewed
    stitch_reviewed --> [*]
    @enduml

    lock_state
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
    stitched_left = models.BooleanField(default=False)
    stitched_right = models.BooleanField(default=False)
    state = FSMField(default='empty', protected=True)
    lock_state = FSMField(default='unlocked', protected=True)

    objects = TranscriptFragmentManager()

    class Meta:
        ordering = ('start',)
        unique_together = [
            ('transcript', 'start', 'end'),
        ]

    def stitched_both_sides(self):
        return self.stitched_left and self.stitched_right

    @transition(lock_state, 'unlocked', 'locked', save=True)
    def lock(self):
        pass

    @transition(lock_state, 'locked', 'unlocked', save=True)
    def unlock(self):
        pass

    @transition(state, 'empty', 'transcribed', save=True)
    def transcribe(self):
        pass

    @transition(state, 'transcribed', 'transcript_reviewed', save=True)
    def review_transcript(self):
        pass

    @transition(state, 'transcript_reviewed', 'stitched', save=True,
                conditions=[stitched_both_sides])
    def stitch(self):
        pass

    @transition(state, 'stitched', 'stitch_reviewed', save=True,
                conditions=[stitched_both_sides])
    def review_stitch(self):
        self._merge_sentences()
        self._complete_sentences()

    def _merge_sentences(self):
        """Merge overlapping Sentence instances."""
        latest_revision = self.revisions.latest()
        deletion_candidates = []
        for sf in latest_revision.sentence_fragments.all():
            sentences = sf.sentences
            candidate_sentences = sf.candidate_sentences
            if sentences.count() > 1 or candidate_sentences.count() > 1:
                # This fragment is in more than one sentence.
                # Pick the first sentence selected as the survivor.
                if sentences:
                    survivor = sentences.first()
                else:
                    survivor = candidate_sentences.first()

                def merge(s, o):
                    s.fragments.add(*o.fragments.all())
                    s.fragment_candidates.add(
                        *o.fragment_candidates.all())
                    o.delete()

                for other in sentences.all():
                    if other != survivor:
                        merge(survivor, other)

                for other in candidate_sentences.all():
                    print 'other', other
                    if other != survivor:
                        merge(survivor, other)

    def _complete_sentences(self):
        """Complete sentences in this fragment as applicable."""
        print 'completing sentences for', self.start, self.end
        latest = self.revisions.latest()
        for candidate_sf in latest.sentence_fragments.all():
            print '  candidate_sf', candidate_sf.text
            for sentence in candidate_sf.sentences.filter(state='partial'):
                print '    sentence', sentence.id, sentence.text
                if sentence.fragment_candidates.count() > 0:
                    # The sentence is still being worked on.
                    continue
                if all(
                    other_sf.revision.fragment.state == 'stitch_reviewed'
                    for other_sf in sentence.fragments.all()
                    if other_sf != candidate_sf
                ):
                    sentence.complete()


# ---------------------


class TranscriptFragmentRevision(TimeStampedModel):
    """A revision of a TranscriptFragment."""

    fragment = models.ForeignKey('TranscriptFragment', related_name='revisions')
    sequence = models.PositiveIntegerField()
    editor = models.ForeignKey('auth.User')

    class Meta:
        get_latest_by = 'sequence'
        ordering = ('sequence',)
        unique_together = [
            ('fragment', 'sequence'),
        ]

    @property
    def text(self):
        return '\n\n'.join(
            sf.text for sf in self.sentence_fragments.all())


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
