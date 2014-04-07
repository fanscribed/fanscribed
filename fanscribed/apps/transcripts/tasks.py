from decimal import Decimal
import time

from celery.app import shared_task
from celery.exceptions import Reject

from ..media import avlib
from ..media.models import MediaFile
from ..media.storage import new_local_mediafile_path


# These settings are optimal for creating single-channel,
# 44.1KHz, 64k bitstream MP3 audio files.
PROCESSED_MEDIA_AVCONV_SETTINGS = [
    '-ac', '1',
    '-ar', '44100',
    '-b', '64k',
    '-c:a', 'libmp3lame',
    '-f', 'mp2',
]


# =====================


@shared_task
def create_processed_transcript_media(transcript_media_pk):

    from .models import TranscriptMedia

    raw_transcript_media = TranscriptMedia.objects.get(pk=transcript_media_pk)
    transcript = raw_transcript_media.transcript

    # Fail if processed already.
    if raw_transcript_media.is_processed:
        # TODO: What's a better exception class?
        raise Exception('Cannot process already-processed media.')

    # Fail if not full-length.
    if not raw_transcript_media.is_full_length:
        # TODO: What's a better exception class?
        raise Exception('Cannot process media that is not full length.')

    # Succeed if we've already converted it.
    processed_media = dict(
        transcript=transcript,
        is_processed=True,
        is_full_length=True,
    )
    if TranscriptMedia.objects.filter(**processed_media).exists():
        return

    # Convert raw media to processed audio.
    raw_file = raw_transcript_media.media_file.local_cache_path()
    processed_file = new_local_mediafile_path()
    avlib.convert(raw_file, processed_file, PROCESSED_MEDIA_AVCONV_SETTINGS)

    # Find length of raw media.
    raw_length = avlib.media_length(raw_file)
    raw_transcript_media.start = 0.00
    raw_transcript_media.end = raw_length
    raw_transcript_media.save()

    # Find length of processed media.
    processed_length = avlib.media_length(processed_file)
    processed_media_file = MediaFile.objects.create(
        data_url='file://{processed_file}'.format(**locals()),
    )
    processed_transcript_media = TranscriptMedia.objects.create(
        transcript=transcript,
        media_file=processed_media_file,
        is_processed=True,
        is_full_length=True,
        start=0.00,
        end=processed_length,
    )

    # Set transcript's length based on processed media.
    transcript.set_length(processed_transcript_media.end)


# =====================


def _get_task(task_class, pk):
    task = task_class.objects.get(pk=pk)
    if task.state == 'presented':
        time.sleep(0.1)  # wait for database to propagate
        task = task_class.objects.get(pk=pk)
    if task.state != 'submitted':
        raise Reject('Task not in "submitted" state.')
    return task


# ---------------------


@shared_task
def process_transcribe_task(pk):

    from .models import TranscribeTask, SentenceFragment

    task = _get_task(TranscribeTask, pk)

    # Require text.
    if task.text is None or task.text.strip() == u'':
        print 'transcribe: no text'
        task.invalidate()
        return

    # Clean up text.
    lines = [L.strip() for L in task.text.strip().split(u'\n') if L.strip()]
    for sequence, line in enumerate(lines, 1):
        SentenceFragment.objects.create(
            revision=task.revision,
            sequence=sequence,
            text=line,
        )

    # Compare revisions and update TranscriptFragment state.
    if not task.is_review:
        task.revision.fragment.transcribe()
    else:
        # Compare revisions.
        last_revision = task.revision.fragment.revisions.get(
            sequence=task.revision.sequence - 1)
        if task.revision.text != last_revision.text:
            # They differ;
            # keep at transcribed to allow for further review.
            pass
        else:
            # They are the same; finish reviewing.
            task.revision.fragment.review()

    task.validate()


# ---------------------


@shared_task
def process_stitch_task(pk):

    from .models import SentenceFragment, StitchTask

    task = _get_task(StitchTask, pk)

    left_fragment_revision = task.stitch.left.revisions.latest()
    right_fragment_revision = task.stitch.right.revisions.latest()

    if not task.is_review:
        old_pairings = set([])
    else:
        # Detect prior pairings.
        old_pairings = set([
            # (left_sentence_fragment_id, right_sentence_fragment_id),
        ])
        for left_fragment in left_fragment_revision.sentence_fragments.all():
            for left_sentence in left_fragment.candidate_sentences.all():
                left_sf = None
                right_sf = None
                for candidate in left_sentence.fragment_candidates.all():
                    if candidate.revision == left_fragment_revision:
                        left_sf = candidate
                    if candidate.revision == right_fragment_revision:
                        right_sf = candidate
                if left_sf is not None and right_sf is not None:
                    old_pairings.add((left_sf.id, right_sf.id))

    # Create new pairings.
    new_pairings = set([
        # (left_sentence_fragment_id, right_sentence_fragment_id),
    ])
    # Make sure every fragment has a sentence.
    def _make_sentence(sentence_fragment):
        if (sentence_fragment.candidate_sentences.count() == 0
            and sentence_fragment.sentences.count() == 0
            ):
            s = task.transcript.sentences.create(
                tf_start=sentence_fragment.revision.fragment,
                tf_sequence=sentence_fragment.sequence,
            )
            s.add_candidates(sentence_fragment)
    for sf in left_fragment_revision.sentence_fragments.all():
        _make_sentence(sf)
    right_is_at_end = (task.stitch.right.end == task.transcript.length)
    if right_is_at_end:
        print '** RIGHT IS AT END'
        # Special case when the right side is the last TranscriptFragment.
        for sf in right_fragment_revision.sentence_fragments.all():
            print 'sf', sf.text
            _make_sentence(sf)

    for pairing in task.pairings.all():
        print 'adding new_pairing', (pairing.left.text, pairing.right.text)
        new_pairings.add((pairing.left.id, pairing.right.id))

    # Add new pairings.
    for left_sf_id, right_sf_id in new_pairings - old_pairings:
        left_sf = SentenceFragment.objects.get(id=left_sf_id)
        right_sf = SentenceFragment.objects.get(id=right_sf_id)
        if left_sf.candidate_sentences.count():
            left_sf.candidate_sentences.first().add_candidates(right_sf)
        elif right_sf.candidate_sentences.count():
            right_sf.candidate_sentences.first().add_candidates(left_sf)
        elif left_sf.sentences.count():
            left_sf.sentences.first().add_candidates(right_sf)
        else:
            right_sf.sentences.first().add_candidates(left_sf)

    # Delete removed pairings.
    for left_sf_id, right_sf_id in old_pairings - new_pairings:
        left_sf = SentenceFragment.objects.get(id=left_sf_id)
        right_sf = SentenceFragment.objects.get(id=right_sf_id)
        for sentence in left_sf.candidate_sentences.all():
            sentence.remove_candidates(right_sf)
            # Delete orphaned sentences.
            if (sentence.fragments.count() == 0
                and sentence.fragment_candidates.count() == 0
                ):
                sentence.delete()
        if right_is_at_end:
            for sentence in right_sf.candidate_sentences.all():
                sentence.remove_candidates(left_sf)
                # Delete orphaned sentences.
                if (sentence.fragments.count() == 0
                    and sentence.fragment_candidates.count() == 0
                ):
                    sentence.delete()
        # Recreate sentences for orphaned fragments.
        if right_sf.candidate_sentences.count() == 0:
            _make_sentence(right_sf)
        if left_sf.candidate_sentences.count() == 0:
            _make_sentence(left_sf)

    fragment_left = task.stitch.left
    fragment_right = task.stitch.right
    if not task.is_review:
        # First time.
        task.stitch.stitch()

    elif task.is_review and old_pairings == new_pairings:
        if right_is_at_end: print '-- review'
        # No changes; commit sentence candidates.
        # TODO: review if-statement conditions
        if True or fragment_left.stitched_left:
            for sf in left_fragment_revision.sentence_fragments.all():
                if sf.revision.fragment == fragment_left:
                    for sentence in sf.candidate_sentences.all():
                        sentence.commit_candidates(sf)
        if True or fragment_right.stitched_right:
            for sf in right_fragment_revision.sentence_fragments.all():
                if sf.revision.fragment == fragment_right:
                    for sentence in sf.candidate_sentences.all():
                        if right_is_at_end: print '-- commit', sf.id, 'to', sentence.id
                        sentence.commit_candidates(sf)

        task.stitch.review()

    else:
        # Changes detected; review one more time.
        print '-- review, changes detected:'
        print 'old_pairings', old_pairings
        print 'new_pairings', new_pairings
        pass

    task.validate()


# ---------------------


@shared_task
def process_clean_task(pk):

    from .models import CleanTask

    task = _get_task(CleanTask, pk)

    # Require text.
    if task.text is None or task.text.strip() == u'':
        print 'clean: no text'
        task.invalidate()
        return

    # Clean up text.
    text = task.text.strip()

    # Update sentence.
    sequence = task.sentence.revisions.latest().sequence + 1
    task.sentence.revisions.create(
        sequence=sequence,
        editor=task.assignee,
        text=text,
    )

    task.validate()


# ---------------------


@shared_task
def process_boundary_task(pk):

    from .models import BoundaryTask

    task = _get_task(BoundaryTask, pk)

    # Require start and end.
    if task.start is None or task.end is None:
        print 'start or end is none:', (task.start, task.end)
        task.invalidate()
        return

    # Require end to be > start.
    if task.end <= task.start:
        print 'end is <= start:', (task.start, task.end)
        task.invalidate()
        return

    # Require start and end to be within transcript.
    if task.start < Decimal('0') or task.end > task.transcript.length:
        print 'start or end is out of bounds:', (task.start, task.end)
        task.invalidate()
        return

    # Update sentence.
    if not task.is_review:
        sequence = 1
    else:
        sequence = task.sentence.boundaries.latest().sequence + 1
    task.sentence.boundaries.create(
        sequence=sequence,
        editor=task.assignee,
        start=task.start,
        end=task.end,
    )

    task.validate()


# ---------------------


@shared_task
def process_speaker_task(pk):

    from .models import Speaker, SpeakerTask

    task = _get_task(SpeakerTask, pk)

    # Require speaker XOR speaker name
    has_new_name = (task.new_name is not None and task.new_name.strip() != u'')
    if ((task.speaker is None and not has_new_name)
        or (task.speaker is not None and has_new_name)
        ):
        print 'speaker XOR speaker name not given'
        task.invalidate()
        return

    # Update sentence.
    if not task.is_review:
        sequence = 1
    else:
        sequence = task.sentence.speakers.latest().sequence + 1

    if has_new_name:
        task.speaker = Speaker.objects.create(
            transcript=task.transcript,
            name=task.new_name,
        )

    task.sentence.speakers.create(
        sequence=sequence,
        editor=task.assignee,
        speaker=task.speaker,
    )

    task.validate()
