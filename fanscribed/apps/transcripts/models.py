import logging
log = logging.getLogger(__name__)

import datetime
from decimal import Decimal
import re
import unicodedata

from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.timezone import utc
from django_fsm.db.fields import FSMField, transition
from django_fsm.signals import pre_transition, post_transition
from model_utils.models import TimeStampedModel
from redis_cache import get_redis_connection
from waffle import flag_is_active

from ... import locks


# ================================================================
#                           TRANSCRIPTS
# ================================================================


class SentenceManager(models.Manager):

    use_for_related_fields = True

    def empty(self):
        return self.filter(state='empty')

    def partial(self):
        return self.filter(state='partial')

    def completed(self):
        return self.filter(state='completed')

    def clean_edited(self):
        return self.filter(clean_state='edited')

    def clean_reviewed(self):
        return self.filter(clean_state='reviewed')

    def boundary_edited(self):
        return self.filter(boundary_state='edited')

    def boundary_reviewed(self):
        return self.filter(boundary_state='reviewed')

    def speaker_edited(self):
        return self.filter(speaker_state='edited')

    def speaker_reviewed(self):
        return self.filter(speaker_state='reviewed')


class Sentence(models.Model):
    """A sentence made from sentence fragments.

    state
    -----

    @startuml
    [*] --> empty
    empty --> partial
    partial --> completed
    completed --> [*]
    @enduml

    clean_state, boundary_state, speaker_state
    ------------------------------------------

    These are all unprotected fields, and have no transition methods.
    We trust ourselves to change them appropriately instead.

    @startuml
    [*] --> untouched
    untouched --> editing
    editing --> untouched
    editing --> edited
    edited --> reviewing
    reviewing --> edited
    reviewing --> reviewed
    @enduml
    """

    transcript = models.ForeignKey('Transcript', related_name='sentences')
    state = FSMField(default='empty', protected=True)

    clean_state = FSMField(default='untouched')     # Not protected.
    clean_lock_id = models.CharField(max_length=32, blank=True, null=True)
    clean_last_editor = models.ForeignKey('auth.User', blank=True, null=True, related_name='+')

    boundary_state = FSMField(default='untouched')  # Not protected.
    boundary_lock_id = models.CharField(max_length=32, blank=True, null=True)
    boundary_last_editor = models.ForeignKey('auth.User', blank=True, null=True, related_name='+')

    speaker_state = FSMField(default='untouched')   # Not protected.
    speaker_lock_id = models.CharField(max_length=32, blank=True, null=True)
    speaker_last_editor = models.ForeignKey('auth.User', blank=True, null=True, related_name='+')

    fragments = models.ManyToManyField(
        'SentenceFragment', related_name='sentences')
    fragment_candidates = models.ManyToManyField(
        'SentenceFragment', related_name='candidate_sentences')
    tf_start = models.ForeignKey('TranscriptFragment')
    tf_sequence = models.PositiveIntegerField()
    latest_text = models.TextField(blank=True, null=True)
    latest_start = models.DecimalField(max_digits=8, decimal_places=2,
                                       blank=True, null=True)
    latest_end = models.DecimalField(max_digits=8, decimal_places=2,
                                     blank=True, null=True)
    latest_speaker = models.ForeignKey('Speaker', blank=True, null=True)

    class Meta:
        ordering = ('tf_start__start', 'tf_sequence')

    objects = SentenceManager()

    def __unicode__(self):
        return u'{self.state} sentence'.format(**locals())

    @property
    def text(self):
        return u' '.join(fragment.text for fragment in self.fragments.all())

    @property
    def candidate_text(self):
        return u' '.join(
            fragment.text for fragment in self.fragment_candidates.all())

    # --

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
        # Set initial latest text and (latest_start, latest_end).
        self.revisions.create(
            sequence=1,
            text=self.text,
        )
        starts = set()
        ends = set()
        for fragment in self.fragments.all():
            transcript_fragment = fragment.revision.fragment
            starts.add(transcript_fragment.start)
            ends.add(transcript_fragment.end)
        self.latest_start = min(starts)
        self.latest_end = max(ends)

    # --

    @property
    def _clean_lockname(self):
        return 'lock:sc:{self.id}'.format(**locals())

    @property
    def _boundary_lockname(self):
        return 'lock:sb:{self.id}'.format(**locals())

    @property
    def _speaker_lockname(self):
        return 'lock:ss:{self.id}'.format(**locals())

    def lock_clean(self):
        locks.acquire_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._clean_lockname,
            lockid_field='clean_lock_id',
        )

    def unlock_clean(self):
        locks.release_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._clean_lockname,
            lockid_field='clean_lock_id',
        )

    def lock_boundary(self):
        locks.acquire_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._boundary_lockname,
            lockid_field='boundary_lock_id',
        )

    def unlock_boundary(self):
        locks.release_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._boundary_lockname,
            lockid_field='boundary_lock_id',
        )

    def lock_speaker(self):
        locks.acquire_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._speaker_lockname,
            lockid_field='speaker_lock_id',
        )

    def unlock_speaker(self):
        locks.release_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._speaker_lockname,
            lockid_field='speaker_lock_id',
        )


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


class SentenceRevision(models.Model):
    """A full-text revision of a sentence."""

    sentence = models.ForeignKey('Sentence', related_name='revisions')
    sequence = models.PositiveIntegerField()
    editor = models.ForeignKey('auth.User', blank=True, null=True)
    text = models.TextField()

    class Meta:
        ordering = ('sequence',)
        get_latest_by = 'sequence'
        unique_together = [
            ('sentence', 'sequence'),
        ]


@receiver(post_save, sender=SentenceRevision)
def update_sentence_latest_text(instance, created, raw, **kwargs):
    if created and not raw:
        sentence = instance.sentence
        sentence.latest_text = instance.text
        sentence.save()


# ---------------------


class SentenceBoundary(models.Model):
    """A precise start/end boundary of a sentence."""

    sentence = models.ForeignKey('Sentence', related_name='boundaries')
    sequence = models.PositiveIntegerField()
    editor = models.ForeignKey('auth.User')
    start = models.DecimalField(max_digits=8, decimal_places=2)
    end = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ('sequence',)
        get_latest_by = 'sequence'
        unique_together = [
            ('sentence', 'sequence'),
        ]


@receiver(post_save, sender=SentenceBoundary)
def update_sentence_latest_boundary(instance, created, raw, **kwargs):
    if created and not raw:
        sentence = instance.sentence
        sentence.latest_start = instance.start
        sentence.latest_end = instance.end
        sentence.save()


# ---------------------


class Speaker(models.Model):
    """A unique speaker in the transcript."""

    transcript = models.ForeignKey('Transcript', related_name='speakers')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = [
            ('transcript', 'name'),
        ]

    def __unicode__(self):
        return self.name


# ---------------------


class TranscriptManager(models.Manager):

    use_for_related_fields = True

    def unfinished(self):
        return self.filter(state='unfinished')

    def finished(self):
        return self.filter(state='finished')

    def without_known_length(self):
        return self.filter(length_state='unset')

    def with_known_length(self):
        return self.filter(length_state='set')


class Transcript(TimeStampedModel):
    """A transcript of audio or video to text.

    state
    -----

    @startuml
    [*] --> unfinished
    unfinished --> finished
    finished --> [*]
    @enduml

    length_state
    ------------

    @startuml
    [*] --> unset
    unset --> set
    set --> [*]
    @enduml
    """

    title = models.CharField(max_length=512)
    state = FSMField(default='unfinished', protected=True)
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    length_state = FSMField(default='unset', protected=True)
    created_by = models.ForeignKey('auth.User', blank=True, null=True)
    contributors = models.ManyToManyField(
        'auth.User', related_name='contributed_to_transcripts')

    objects = TranscriptManager()

    class Meta:
        get_latest_by = 'created'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'transcripts:detail_slug',
            kwargs=dict(pk=self.pk, slug=slugify(self.title)))

    def _all_tasks_complete(self):
        return all(v == 100 for v in self.stats.values())

    @transition(state, 'unfinished', 'finished', save=True,
                conditions=[_all_tasks_complete])
    def finish(self):
        pass

    @transition(length_state, 'unset', 'set', save=True)
    def set_length(self, length):
        self.length = Decimal(length)
        self._create_fragments()

    def _create_fragments(self):
        start = Decimal('0')
        previous = None
        while start < self.length:

            # Find the end of the current fragment.
            # If remaining time is less than fragment length, stretch to end.
            end = start + settings.TRANSCRIPT_FRAGMENT_LENGTH
            remaining = self.length - end
            if remaining < settings.TRANSCRIPT_FRAGMENT_LENGTH:
                end = self.length

            current = self.fragments.create(
                start=start,
                end=end,
                # # First and last fragments are 'stitched' to each end. :)
                # stitched_left=True if start == Decimal('0') else False,
                # stitched_right=True if end == self.length else False,
            )

            if previous is not None:
                self.stitches.create(
                    left=previous,
                    right=current,
                )

            start = end
            previous = current

    @property
    def completed_sentences(self):
        return self.sentences.filter(state='completed').order_by('latest_start')

    @property
    def processed_media_url(self):
        """Returns the URL for the transcript's full-length processed audio,
        or None if no such audio exists for the transcript."""
        try:
            return self.media.get(is_processed=True, is_full_length=True).file.url
        except TranscriptMedia.DoesNotExist:
            return None

    @property
    def stats(self):
        """Return a dictionary with a percentage of completion of each phase."""
        stats = {}

        fragments_count = self.fragments.count()
        if fragments_count == 0:
            stats.update(transcribe=0)
        else:
            stats['transcribe'] = (
                (self.fragments.transcribed().count() + self.fragments.reviewed().count() * 2) * 100
                /
                (self.fragments.count() * 2)
            )

        stitches_count = self.stitches.count()
        if stitches_count == 0:
            stats.update(stitch=0)
        else:
            stats['stitch'] = (
                (self.stitches.stitched().count() + self.stitches.reviewed().count() * 2) * 100
                /
                (self.stitches.count() * 2)
            )
        
        sentence_count = self.sentences.count()
        if sentence_count == 0:
            stats.update(clean=0, boundary=0, speaker=0)
        else:
            stitch_factor = stats['stitch'] * 0.01
            stats['clean'] = (
                (self.sentences.clean_edited().count() + self.sentences.clean_reviewed().count() * 2) * 100 * stitch_factor
                /
                (sentence_count * 2)
            )
            stats['boundary'] = (
                (self.sentences.boundary_edited().count() + self.sentences.boundary_reviewed().count() * 2) * 100 * stitch_factor
                /
                (sentence_count * 2)
            )
            stats['speaker'] = (
                (self.sentences.speaker_edited().count() + self.sentences.speaker_reviewed().count() * 2) * 100 * stitch_factor
                /
                (sentence_count * 2)
            )

        return stats


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
    transcribed --> reviewed
    reviewed --> [*]
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
    state = FSMField(default='empty', protected=True)
    lock_state = FSMField(default='unlocked', protected=True)
    lock_id = models.CharField(max_length=32, blank=True, null=True)
    last_editor = models.ForeignKey('auth.User', blank=True, null=True, related_name='+')

    objects = TranscriptFragmentManager()

    class Meta:
        ordering = ('start',)
        unique_together = [
            ('transcript', 'start', 'end'),
        ]

    def stitched_both_sides(self):
        return self.stitched_left and self.stitched_right

    @property
    def _lockname(self):
        return 'lock:tf:{self.id}'.format(**locals())

    @transition(lock_state, 'unlocked', 'locked', save=True)
    def lock(self):
        locks.acquire_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._lockname,
            lockid_field='lock_id',
        )

    @transition(lock_state, 'locked', 'unlocked', save=True)
    def unlock(self):
        locks.release_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._lockname,
            lockid_field='lock_id',
        )

    @transition(state, 'empty', 'transcribed', save=True)
    def transcribe(self):
        pass

    @transition(state, 'transcribed', 'reviewed', save=True)
    def review(self):
        # Ready related stitches if other fragments are transcribed.
        if self.start != Decimal(0):
            L = self.stitch_at_left
            if L.left.state == 'reviewed':
                L.ready()
        if self.end != self.transcript.length:
            R = self.stitch_at_right
            if R.right.state == 'reviewed':
                R.ready()


# ---------------------


class TranscriptStitchManager(models.Manager):

    def notready(self):
        return self.filter(state='notready')

    def unstitched(self):
        return self.filter(state='unstitched')

    def stitched(self):
        return self.filter(state='stitched')

    def reviewed(self):
        return self.filter(state='reviewed')

    def locked(self):
        return self.filter(lock_state='locked')

    def unlocked(self):
        return self.filter(lock_state='unlocked')


class TranscriptStitch(models.Model):
    """A stitch between two fragments of a transcript.

    state
    -----

    @startuml
    [*] --> notready
    notready --> unstitched
    unstitched --> stitched
    stitched --> reviewed
    reviewed --> [*]
    @enduml

    lock_state
    ------------

    @startuml
    [*] --> unlocked
    unlocked --> locked
    locked --> unlocked
    @enduml
    """

    transcript = models.ForeignKey('Transcript', related_name='stitches')
    left = models.OneToOneField('TranscriptFragment', related_name='stitch_at_right')
    right = models.OneToOneField('TranscriptFragment', related_name='stitch_at_left')
    state = FSMField(default='notready', protected=True)
    lock_state = FSMField(default='unlocked', protected=True)
    lock_id = models.CharField(max_length=32, blank=True, null=True)
    last_editor = models.ForeignKey('auth.User', blank=True, null=True, related_name='+')

    objects = TranscriptStitchManager()

    class Meta:
        ordering = ('left__start',)
        unique_together = [
            ('transcript', 'left'),
        ]

    @property
    def _lockname(self):
        return 'lock:ts:{self.id}'.format(**locals())

    @transition(lock_state, 'unlocked', 'locked', save=True)
    def lock(self):
        locks.acquire_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._lockname,
            lockid_field='lock_id',
        )

    @transition(lock_state, 'locked', 'unlocked', save=True)
    def unlock(self):
        locks.release_model_lock(
            conn=get_redis_connection('default'),
            instance=self,
            lockname=self._lockname,
            lockid_field='lock_id',
        )

    @transition(state, 'notready', 'unstitched', save=True)
    def ready(self):
        pass

    @transition(state, 'unstitched', 'stitched', save=True)
    def stitch(self):
        self._merge_sentences()

    @transition(state, 'stitched', 'reviewed', save=True)
    def review(self):
        self._merge_sentences()
        self._complete_sentences()

    def _merge_sentences(self):
        """Merge overlapping Sentence instances."""
        left_fragment_revision = self.left.revisions.latest()
        right_fragment_revision = self.right.revisions.latest()

        for revision in [left_fragment_revision, right_fragment_revision]:
            deletion_candidates = []
            for sf in revision.sentence_fragments.all():
                sentences = sf.sentences
                candidate_sentences = sf.candidate_sentences

                # If fragment is in more than one sentence,
                # pick the first sentence as the survivor.
                if sentences.count() > 1:
                    survivor = sentences.first()
                elif candidate_sentences.count() > 1:
                    survivor = candidate_sentences.first()
                else:
                    survivor = None

                if survivor is not None:
                    # Merge remaining sentences with survivor.
                    def merge(s, o):
                        s.fragments.add(*o.fragments.all())
                        s.fragment_candidates.add(
                            *o.fragment_candidates.all())
                        o.delete()
                    for other in sentences.all():
                        if other != survivor:
                            merge(survivor, other)
                    for other in candidate_sentences.all():
                        if other != survivor:
                            merge(survivor, other)
                else:
                    # No survivor means there was only one sentence involved.
                    pass

    def _complete_sentences(self):
        """Complete sentences in this stitch (when they are ready)."""

        left_fragment_revision = self.left.revisions.latest()
        right_fragment_revision = self.right.revisions.latest()

        # Look for partial sentences in these revisions and complete them.
        revisions_to_complete = [
            left_fragment_revision,
            right_fragment_revision,
        ]

        # Also look for partial sentences in adjacent reviewed stitches.
        if self.left.start != Decimal(0):
            stitch_at_left = TranscriptStitch.objects.get(right=self.left)
            if stitch_at_left.state == 'reviewed':
                revisions_to_complete.append(stitch_at_left.left.revisions.latest())

        if self.right.end != self.transcript.length:
            stitch_at_right = TranscriptStitch.objects.get(left=self.right)
            if stitch_at_right.state == 'reviewed':
                revisions_to_complete.append(stitch_at_right.right.revisions.latest())

        # Complete sentences.
        sentences_checked = set()
        for revision in revisions_to_complete:
            for candidate_sf in revision.sentence_fragments.all():
                for sentence in candidate_sf.sentences.filter(state='partial'):

                    if sentence.id in sentences_checked:
                        # Already checked this sentence ID.
                        continue

                    sentences_checked.add(sentence.id)

                    # Check partial sentence.

                    if sentence.fragment_candidates.count() > 0:
                        # The sentence is still being worked on.
                        continue
                    else:
                        # Complete the sentence if all related stitches
                        # are reviewed, AND adjacent stitches are reviewed.
                        for other_sf in sentence.fragments.all():
                            if True or other_sf != candidate_sf:
                                other_tf = other_sf.revision.fragment
                                must_be_reviewed = set()

                                # Find each stitch related to the sentence
                                # fragment, and its neighbor.
                                try:
                                    stitch_at_left = other_tf.stitch_at_left
                                    must_be_reviewed.add(stitch_at_left)
                                    left_of_left = TranscriptStitch.objects.get(
                                        right=stitch_at_left.left)
                                    must_be_reviewed.add(left_of_left)
                                except TranscriptStitch.DoesNotExist:
                                    pass

                                try:
                                    stitch_at_right = other_tf.stitch_at_right
                                    must_be_reviewed.add(stitch_at_right)
                                    right_of_right = TranscriptStitch.objects.get(
                                        left=stitch_at_right.right)
                                    must_be_reviewed.add(right_of_right)
                                except TranscriptStitch.DoesNotExist:
                                    pass

                                # Ignore the stitch currently being reviewed.
                                if self in must_be_reviewed:
                                    must_be_reviewed.remove(self)

                                states = [s.state for s in must_be_reviewed]
                                if any(state != 'reviewed' for state in states):
                                    # Not completing.
                                    break
                                else:
                                    # May complete.
                                    pass
                        else:
                            # All stitches involved in the sentence
                            # are reviewed.
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


# ================================================================
#                            MEDIA
# ================================================================


class TranscriptMedia(TimeStampedModel):
    """
    @startuml
    [*] --> empty
    empty --> creating
    creating --> ready
    ready --> deleted
    deleted --> creating
    @enduml
    """

    transcript = models.ForeignKey('transcripts.Transcript', related_name='media')
    file = models.FileField(upload_to='transcripts', max_length=1024)
    state = FSMField(default='empty', protected=True)
    is_processed = models.BooleanField(help_text='Is it processed media?')
    is_full_length = models.BooleanField(
        help_text='Is it the full length of media to be transcribed?')
    start = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    end = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    download_count = models.PositiveIntegerField(default=0)

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

    def create_processed_task(self):
        """Create a processed TranscriptMedia based on this one.

        Assumes that this one is raw and full-length.
        """
        from .tasks import create_processed_transcript_media
        return create_processed_transcript_media.delay(self.pk)

    def create_file_task(self):
        """Create a file for this TranscriptMedia."""
        from .tasks import create_transcript_media_file
        return create_transcript_media_file.delay(self.pk)

    def record_download(self):
        self.download_count += 1
        self.save()

    @transition(state, ['empty', 'deleted'], 'creating', save=True)
    def create_file(self):
        pass

    def has_file(self):
        return bool(self.file)

    @transition(state, 'creating', 'ready', save=True, conditions=[has_file])
    def finish(self):
        pass

    @transition(state, 'ready', 'deleted', save=True)
    def delete_file(self):
        self.file.delete()


# ================================================================
#                            TASKS
# ================================================================


def existing_transcript_task(transcript, user):
    """Check for existing tasks in this transcript."""
    for task_class in TASK_MODEL.values():
        existing_tasks = task_class.objects.filter(
            transcript=transcript,
            assignee=user,
            state='presented',
        )
        if existing_tasks:
            return existing_tasks[0]


def assign_next_transcript_task(transcript, user, requested_task_type, request=None):
    """Try to create the next available task of the requested type."""

    # Determine which order to search for available tasks.
    if requested_task_type == 'any_sequential':
        # Sequential moves through the pipeline in one stage at a time.
        L = [
            # (task_type, is_review),
            ('transcribe', False),
            ('transcribe', True),
            ('stitch', False),
            ('stitch', True),
            ('boundary', False),
            ('boundary', True),
            ('clean', False),
            ('clean', True),
            ('speaker', False),
            ('speaker', True),
        ]
    elif requested_task_type == 'any_eager':
        # Eager switches you to a new task type as soon as one is available.
        L = [
            # (task_type, is_review),
            ('boundary', True),
            ('clean', True),
            ('speaker', True),
            ('boundary', False),
            ('clean', False),
            ('speaker', False),
            ('stitch', True),
            ('stitch', False),
            ('transcribe', True),
            ('transcribe', False),
        ]
    else:
        # An individual task type was selected.
        if requested_task_type.endswith('_review'):
            # Remove '_review' from requested task type.
            requested_task_type = requested_task_type.split('_review')[0]
            is_review = True
        else:
            # No changes to requested task type.
            is_review = False
        L = [(requested_task_type, is_review)]

    preferred_task_types = user.profile.preferred_task_names
    for task_type, is_review in L:

        # Does the user want to perform this kind of task?
        if task_type not in preferred_task_types:
            continue
        if is_review and not user.profile.wants_reviews:
            continue

        # Does the user have permission to perform the task?
        perm_name = 'transcripts.add_{}task{}'.format(
            task_type,
            '_review' if is_review else '',
        )
        if not user.has_perm(perm_name):
            continue

        # Permission granted; try to create this type of task.
        tasks = TASK_MODEL[task_type].objects
        if tasks.can_create(user, transcript, is_review, request):
            # Try to get this kind of task,
            # ignoring lock failures up to 5 times.
            for x in xrange(5):
                try:
                    task = tasks.create_next(user, transcript, is_review, request)
                except locks.LockException:
                    # Try again.
                    continue
                else:
                    if task is not None:
                        task.present()
                        return task


def request_bypasses_teamwork(request):
    return (request is not None
            and request.user.is_superuser
            and flag_is_active(request, 'bypass_teamwork'))


class TaskManager(models.Manager):

    use_for_related_fields = True

    def presented(self):
        return self.filter(state='presented')

    def valid(self):
        return self.filter(state='valid')

    def invalid(self):
        return self.filter(state='invalid')

    def can_create(self, user, transcript, is_review, request=None):
        """Can we create a new task?

        :ptype user: django.contrib.auth.models.User
        :ptype transcript: Transcript
        :ptype review: bool
        """
        return False

    def create_next(self, user, transcript, is_review, request=None):
        """Create and return the next new task.

        :ptype user: django.contrib.auth.models.User
        :ptype transcript: Transcript
        :ptype review: bool
        """
        raise Task.DoesNotExist()


class Task(TimeStampedModel):
    """A transcription task to be completed.

    state
    -----

    @startuml

    [*] --> preparing
    preparing --> ready
    ready --> assigned
    assigned --> presented
    presented --> submitted
    submitted --> valid
    valid --> [*]

    submitted --> invalid
    invalid --> [*]

    presented --> expired
    assigned --> expired
    expired --> [*]

    presented --> canceled
    canceled --> [*]

    @enduml
    """

    transcript = models.ForeignKey('Transcript')
    is_review = models.BooleanField()
    state = FSMField(default='preparing', protected=True)
    assignee = models.ForeignKey('auth.User', blank=True, null=True)
    media = models.ForeignKey('TranscriptMedia', blank=True, null=True)
    presented_at = models.DateTimeField(blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    objects = TaskManager()

    def get_absolute_url(self):
        return reverse('transcripts:task_perform', kwargs=dict(
            transcript_pk=self.transcript.pk,
            type=self.TASK_TYPE,
            pk=self.pk,
        ))

    def finish_transcript_if_all_tasks_complete(self):
        if self.transcript._all_tasks_complete():
            self.transcript.finish()

    def lock(self):
        raise NotImplementedError()

    @transition(state, 'preparing', 'ready', save=True)
    def prepare(self):
        pass

    @transition(state, 'ready', 'assigned', save=True)
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
        if not settings.TESTING:
            self._submit()

    def _submit(self):
        raise NotImplementedError()

    @transition(state, 'submitted', 'valid', save=True)
    def validate(self):
        self._validate()
        self.transcript.contributors.add(self.assignee)

    def _validate(self):
        raise NotImplementedError()

    @transition(state, 'submitted', 'invalid', save=True)
    def invalidate(self):
        self._invalidate()

    @transition(state, ['assigned', 'presented'], 'expired', save=True)
    def expire(self):
        self._invalidate()

    @transition(state, 'presented', 'canceled', save=True)
    def cancel(self):
        self._invalidate()

    def _invalidate(self):
        raise NotImplementedError()


# ---------------------


class TranscribeTaskManager(TaskManager):

    def _available_fragments(self, user, transcript, is_review, request=None):
        if not is_review:
            fragments = transcript.fragments.filter(
                state='empty',
                lock_state='unlocked',
            )
        else:
            fragments = transcript.fragments.filter(
                state='transcribed',
                lock_state='unlocked',
            )

        if settings.TRANSCRIPTS_REQUIRE_TEAMWORK and not request_bypasses_teamwork(request):
            fragments = fragments.exclude(last_editor=user)

        return fragments

    def can_create(self, user, transcript, is_review, request=None):
        return bool(self._available_fragments(user, transcript, is_review, request).count())

    def create_next(self, user, transcript, is_review, request=None):
        fragment = self._available_fragments(user, transcript, is_review, request).first()
        if fragment is None:
            return None

        # Apply overlap.
        start = fragment.start - settings.TRANSCRIPT_FRAGMENT_OVERLAP
        end = fragment.end + settings.TRANSCRIPT_FRAGMENT_OVERLAP

        # Correct for out of bounds.
        start = max(Decimal('0.00'), start)
        end = min(transcript.length, end)

        task = transcript.transcribetask_set.create(
            is_review=is_review,
            media=None,
            fragment=fragment,
            start=fragment.start,
            end=fragment.end,
        )

        try:
            task.lock()
        except locks.LockException:
            task.delete()
            raise

        if not is_review:
            next = fragment.revisions.create(sequence=1, editor=user)
            text = ''
        else:
            latest = fragment.revisions.latest()
            text = latest.text
            next = fragment.revisions.create(sequence=latest.sequence + 1,
                                             editor=user)

        media, created = transcript.media.get_or_create(
            is_processed=True,
            is_full_length=False,
            start=start,
            end=end,
        )

        task.media = media
        task.revision = next
        task.text = text

        task.prepare()
        task.assign_to(user)
        return task


class TranscribeTask(Task):

    TASK_TYPE = 'transcribe'

    fragment = models.ForeignKey('TranscriptFragment', blank=True, null=True)
    revision = models.ForeignKey('TranscriptFragmentRevision',
                                 blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    # Keep start and end even if `revision` goes away.
    start = models.DecimalField(max_digits=8, decimal_places=2)
    end = models.DecimalField(max_digits=8, decimal_places=2)

    objects = TranscribeTaskManager()

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('add_transcribetask_review', 'Can add review transcribe task'),
        )

    def lock(self):
        self.fragment.lock()

    def _assign_to(self):
        pass

    def _submit(self):
        from .tasks import process_transcribe_task
        result = process_transcribe_task.delay(self.pk)

    def _validate(self):
        self.fragment.last_editor = self.assignee
        self.fragment.unlock()

    def _invalidate(self):
        self.revision.delete()
        self.revision = None
        self.fragment.unlock()


# ---------------------


class StitchTaskManager(TaskManager):

    def _available_stitches(self, user, transcript, is_review, request=None):
        if not is_review:
            stitches = transcript.stitches.filter(
                state='unstitched',
                lock_state='unlocked',
            )
        else:
            stitches = transcript.stitches.filter(
                state='stitched',
                lock_state='unlocked',
            )

        if settings.TRANSCRIPTS_REQUIRE_TEAMWORK and not request_bypasses_teamwork(request):
            stitches = stitches.exclude(last_editor=user)

        return stitches

    def can_create(self, user, transcript, is_review, request=None):
        return bool(self._available_stitches(user, transcript, is_review, request).count())

    def create_next(self, user, transcript, is_review, request=None):
        stitch = self._available_stitches(user, transcript, is_review, request).first()
        if not stitch:
            return None

        # Apply overlap.
        start = stitch.left.start - settings.TRANSCRIPT_FRAGMENT_OVERLAP
        end = stitch.right.end + settings.TRANSCRIPT_FRAGMENT_OVERLAP

        # Correct for out of bounds.
        start = max(Decimal('0.00'), start)
        end = min(transcript.length, end)

        media, created = transcript.media.get_or_create(
            is_processed=True,
            is_full_length=False,
            start=start,
            end=end,
        )
        task = transcript.stitchtask_set.create(
            is_review=is_review,
            media=media,
            stitch=stitch,
        )

        try:
            task.lock()
        except locks.LockException:
            task.delete()
            raise

        if is_review:
            task.create_pairings_from_prior_task()

        task.prepare()
        task.assign_to(user)
        return task


class StitchTask(Task):

    TASK_TYPE = 'stitch'

    stitch = models.ForeignKey('TranscriptStitch', related_name='+')

    objects = StitchTaskManager()

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        permissions = (
            ('add_stitchtask_review', 'Can add review stitch task'),
        )

    def lock(self):
        self.stitch.lock()

    def _assign_to(self):
        pass

    def _submit(self):
        from .tasks import process_stitch_task
        process_stitch_task.delay(self.pk)

    def _validate(self):
        self.stitch.last_editor = self.assignee
        self.stitch.unlock()

    def _invalidate(self):
        self.stitch.unlock()

    def create_pairings_from_prior_task(self):
        # Create StitchTaskPairings based on previous completed task.
        previous_completed_task = StitchTask.objects.filter(
            state='valid',
            stitch=self.stitch,
        ).latest()
        for previous_pairing in previous_completed_task.pairings.all():
            self.pairings.get_or_create(
                left=previous_pairing.left,
                right=previous_pairing.right,
            )

    def suggested_pairs(self):
        """Return a list of suggested (left, right) sentence fragment pairs."""

        suggestions = [
            # (left_sentence_fragment_id, right_sentence_fragment_id),
        ]

        stitch = self.stitch
        left_sentence_fragments = stitch.left.revisions.latest().sentence_fragments.all()
        right_sentence_fragments = stitch.right.revisions.latest().sentence_fragments.all()

        def normify(text):
            text = unicodedata.normalize('NFKD', text)
            text = re.sub(ur'[^\w\s:\)-]', u'', text).strip().lower()
            return re.sub(ur'[ \s]+', u' ', text)

        for left_sf in left_sentence_fragments:
            left_text = left_sf.text
            left_norm = normify(left_text)
            left_words = left_norm.split(' ')

            for right_sf in right_sentence_fragments:
                right_text = right_sf.text

                if left_text.startswith('[m]') and right_text.startswith('[m]'):
                    # Both start with music; suggest.
                    suggestions.append((left_sf.id, right_sf.id))
                    continue

                right_norm = normify(right_text)
                right_words = right_norm.split(' ')

                for i in range(len(left_words)):
                    left_partial_norm = ' '.join(left_words[i:])
                    if right_norm.startswith(left_partial_norm):
                        # Potential overlap of text; suggest.
                        suggestions.append((left_sf.id, right_sf.id))
                        break

        return suggestions


class StitchTaskPairing(models.Model):

    task = models.ForeignKey('StitchTask', related_name='pairings')
    left = models.ForeignKey('SentenceFragment', related_name='+')
    right = models.ForeignKey('SentenceFragment', related_name='+')

    class Meta:
        ordering = ('left__revision__fragment__start', 'left__sequence')
        unique_together = [
            ('task', 'left',),
        ]

    def __unicode__(self):
        return 'Pairing between "{self.left.text}" and "{self.right.text}"'.format(**locals())


# ---------------------


class CleanTaskManager(TaskManager):

    def _available_sentences(self, user, transcript, is_review, request=None):
        if not is_review:
            sentences = transcript.sentences.filter(
                state='completed',
                clean_state='untouched',
            )
        else:
            sentences = transcript.sentences.filter(
                state='completed',
                clean_state='edited',
            )

        if settings.TRANSCRIPTS_REQUIRE_TEAMWORK and not request_bypasses_teamwork(request):
            sentences = sentences.exclude(clean_last_editor=user)

        return sentences

    def can_create(self, user, transcript, is_review, request=None):
        return bool(self._available_sentences(user, transcript, is_review, request).count())

    def create_next(self, user, transcript, is_review, request=None):
        sentence = self._available_sentences(user, transcript, is_review, request).first()
        if sentence is None:
            return None

        media, created = transcript.media.get_or_create(
            is_processed=True,
            is_full_length=False,
            start=sentence.latest_start,
            end=sentence.latest_end,
        )

        task = transcript.cleantask_set.create(
            is_review=is_review,
            media=media,
            sentence=sentence,
            text=sentence.latest_text,
        )

        try:
            task.lock()
        except locks.LockException:
            task.delete()
            raise

        task.prepare()
        task.assign_to(user)
        return task


class CleanTask(Task):

    TASK_TYPE = 'clean'

    sentence = models.ForeignKey('Sentence')
    text = models.TextField()

    objects = CleanTaskManager()

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('add_cleantask_review', 'Can add review clean task'),
        )

    def lock(self):
        self.sentence.lock_clean()

    def _assign_to(self):
        if not self.is_review:
            self.sentence.clean_state = 'editing'
        else:
            self.sentence.clean_state = 'reviewing'
        self.sentence.save()

    def _submit(self):
        from .tasks import process_clean_task
        process_clean_task.delay(self.pk)

    def _validate(self):
        if not self.is_review:
            self.sentence.clean_state = 'edited'
        else:
            latest, previous = self.sentence.revisions.order_by('-sequence')[:2]
            if latest.text.strip() == previous.text.strip():
                self.sentence.clean_state = 'reviewed'
            else:
                self.sentence.clean_state = 'edited'
        self.sentence.clean_last_editor = self.assignee
        self.sentence.unlock_clean()
        self.sentence.save()

        self.finish_transcript_if_all_tasks_complete()

    def _invalidate(self):
        if not self.is_review:
            self.sentence.clean_state = 'untouched'
        else:
            self.sentence.clean_state = 'edited'
        self.sentence.unlock_clean()
        self.sentence.save()


# ---------------------


class BoundaryTaskManager(TaskManager):

    def _available_sentences(self, user, transcript, is_review, request=None):
        if not is_review:
            sentences = transcript.sentences.filter(
                state='completed',
                boundary_state='untouched',
            )
        else:
            sentences = transcript.sentences.filter(
                state='completed',
                boundary_state='edited',
            )

        if settings.TRANSCRIPTS_REQUIRE_TEAMWORK and not request_bypasses_teamwork(request):
            sentences = sentences.exclude(boundary_last_editor=user)

        return sentences


    def can_create(self, user, transcript, is_review, request=None):
        return bool(self._available_sentences(user, transcript, is_review, request).count())

    def create_next(self, user, transcript, is_review, request=None):
        sentence = self._available_sentences(user, transcript, is_review, request).first()
        if sentence is None:
            return None

        media_start = sentence.fragments.first().revision.fragment.start - settings.TRANSCRIPT_FRAGMENT_OVERLAP
        media_end = sentence.fragments.last().revision.fragment.end + settings.TRANSCRIPT_FRAGMENT_OVERLAP
        media_start = max(Decimal(0), media_start)
        media_end = min(transcript.length, media_end)

        if not is_review:

            # Apply overlap.
            start = sentence.latest_start - settings.TRANSCRIPT_FRAGMENT_OVERLAP
            end = sentence.latest_end + settings.TRANSCRIPT_FRAGMENT_OVERLAP

            # Correct for out of bounds.
            start = max(Decimal('0.00'), start)
            end = min(transcript.length, end)

            # Find a suggested sentence start:
            # Look for the end of the most recently bounded sentence
            # (ending within the maximum region of this sentence)
            # to try to predict where this sentence will start.
            bounded_sentences = transcript.sentences.completed().filter(
                boundary_state__in=['edited', 'reviewed'],
                latest_end__gt=media_start,
                latest_end__lt=media_end,
            )
            if bounded_sentences.exists():
                latest_bounded = bounded_sentences.order_by('-latest_end')[0]

                # Suggest the end of the last sentence as the start of this one...
                suggested_start = latest_bounded.latest_end

                # ...but only if it comes after the default starting position...
                suggested_start = max(suggested_start, start)

                # ...and only if the calculated starting position comes before
                # the default ending position.
                if suggested_start > end:
                    suggested_start = start

                start = suggested_start

        else:
            # Reviews pass through.
            start = sentence.latest_start
            end = sentence.latest_end

        media, created = transcript.media.get_or_create(
            is_processed=True,
            is_full_length=False,
            start=media_start,
            end=media_end,
        )
        task = transcript.boundarytask_set.create(
            is_review=is_review,
            media=media,
            sentence=sentence,
            start=start,
            end=end,
        )

        try:
            task.lock()
        except locks.LockException:
            task.delete()
            raise

        task.prepare()
        task.assign_to(user)
        return task


class BoundaryTask(Task):

    TASK_TYPE = 'boundary'

    sentence = models.ForeignKey('Sentence')
    start = models.DecimalField(max_digits=8, decimal_places=2)
    end = models.DecimalField(max_digits=8, decimal_places=2)

    objects = BoundaryTaskManager()

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('add_boundarytask_review', 'Can add review boundary task'),
        )

    def lock(self):
        self.sentence.lock_boundary()

    def _assign_to(self):
        if not self.is_review:
            self.sentence.boundary_state = 'editing'
        else:
            self.sentence.boundary_state = 'reviewing'
        self.sentence.save()

    def _submit(self):
        # See below in `process_boundary_task_synchronously_on_submit`.
        pass

    def _validate(self):
        if not self.is_review:
            self.sentence.boundary_state = 'edited'
        else:
            latest, previous = self.sentence.boundaries.order_by('-sequence')[:2]
            if (latest.start, latest.end) == (previous.start, previous.end):
                self.sentence.boundary_state = 'reviewed'
            else:
                self.sentence.boundary_state = 'edited'
        self.sentence.boundary_last_editor = self.assignee
        self.sentence.unlock_boundary()
        self.sentence.save()

        self.finish_transcript_if_all_tasks_complete()

    def _invalidate(self):
        if not self.is_review:
            self.sentence.boundary_state = 'untouched'
        else:
            self.sentence.boundary_state = 'edited'
        self.sentence.unlock_boundary()
        self.sentence.save()


# NOTE: Calls to _submit are normally processed as a celery task,
# but we are interested in getting very quick feedback for new tasks
# as far as predicting the next sentence start.
#
# Therefore, we are running it synchronously here:
#
@receiver(post_transition, sender=BoundaryTask)
def process_boundary_task_synchronously_on_submit(instance, target, **kwargs):
    if target == 'submitted':
        from .tasks import process_boundary_task
        process_boundary_task(instance.pk)


# ---------------------


class SpeakerTaskManager(TaskManager):

    def _available_sentences(self, user, transcript, is_review, request=None):
        if not is_review:
            sentences = transcript.sentences.filter(
                state='completed',
                speaker_state='untouched',
            )
        else:
            sentences = transcript.sentences.filter(
                state='completed',
                speaker_state='edited',
            )

        if settings.TRANSCRIPTS_REQUIRE_TEAMWORK and not request_bypasses_teamwork(request):
            sentences = sentences.exclude(speaker_last_editor=user)

        return sentences


    def can_create(self, user, transcript, is_review, request=None):
        return bool(self._available_sentences(user, transcript, is_review, request).count())

    def create_next(self, user, transcript, is_review, request=None):
        sentence = self._available_sentences(user, transcript, is_review, request).first()
        if sentence is None:
            return None

        start = sentence.latest_start
        media, created = transcript.media.get_or_create(
            is_processed=True,
            is_full_length=False,
            start=sentence.latest_start,
            end=sentence.latest_end,
        )

        task = transcript.speakertask_set.create(
            is_review=is_review,
            media=media,
            sentence=sentence,
            speaker=sentence.latest_speaker,
        )

        try:
            task.lock()
        except locks.LockException:
            task.delete()
            raise

        task.prepare()
        task.assign_to(user)
        return task


class SpeakerTask(Task):

    TASK_TYPE = 'speaker'

    sentence = models.ForeignKey('Sentence')
    speaker = models.ForeignKey('Speaker', blank=True, null=True)
    new_name = models.CharField(max_length=100, blank=True, null=True)

    objects = SpeakerTaskManager()

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('add_speakertask_review', 'Can add review speaker task'),
        )

    def lock(self):
        self.sentence.lock_speaker()

    def _assign_to(self):
        if not self.is_review:
            self.sentence.speaker_state = 'editing'
        else:
            self.sentence.speaker_state = 'reviewing'
        self.sentence.save()

    def _submit(self):
        from .tasks import process_speaker_task
        process_speaker_task.delay(self.pk)

    def _validate(self):
        if not self.is_review:
            self.sentence.speaker_state = 'edited'
        else:
            prior_task = self.sentence.speakertask_set.order_by('-created')[1]
            if self.speaker == prior_task.speaker:
                # No more changes; finished reviewing.
                self.sentence.speaker_state = 'reviewed'
            else:
                # Speaker changed; need to review again.
                self.sentence.speaker_state = 'edited'
        self.sentence.speaker_last_editor = self.assignee
        self.sentence.unlock_speaker()
        self.sentence.save()

        self.finish_transcript_if_all_tasks_complete()

    def _invalidate(self):
        if not self.is_review:
            self.sentence.speaker_state = 'untouched'
        else:
            self.sentence.speaker_state = 'edited'
        self.sentence.unlock_speaker()
        self.sentence.save()


# ---------------------


# Mapping of task types to model classes
TASK_MODEL = {
    # task_type: model_class,
    'transcribe': TranscribeTask,
    'stitch': StitchTask,
    'clean': CleanTask,
    'boundary': BoundaryTask,
    'speaker': SpeakerTask,
}


def track_task_presentation_stats(instance, target, **kwargs):
    utcnow = datetime.datetime.utcnow().replace(tzinfo=utc)
    if target == 'presented':
        instance.presented_at = utcnow
    elif target == 'valid':
        instance.validated_at = utcnow

for _ModelClass in TASK_MODEL.values():
    receiver(pre_transition, sender=_ModelClass)(track_task_presentation_stats)


# ---------------------


@receiver(user_signed_up)
def add_to_workers_group(sender, request, user, **kwargs):
    """The `workers` group has permissions to perform many non-review tasks.

    :ptype user: django.contrib.auth.models.User
    """
    try:
        group = Group.objects.get(name='workers')
    except Group.DoesNotExist:
        log.warning('"workers" group does not exist')
    else:
        user.groups.add(group)
