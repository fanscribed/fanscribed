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


def _get_task(task_class, pk):
    task = task_class.objects.get(pk=pk)
    if task.state == 'presented':
        time.sleep(0.1)  # wait for database to propagate
        task = task_class.objects.get(pk=pk)
    if task.state != 'submitted':
        raise Reject('Task not in "submitted" state.')
    return task


@shared_task
def process_transcribe_task(transcription_task_pk):

    from .models import TranscribeTask, SentenceFragment

    task = _get_task(TranscribeTask, transcription_task_pk)

    # Require text.
    if task.text is None or task.text.strip() == u'':
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
            task.revision.fragment.review_transcript()

    task.validate()


@shared_task
def process_stitch_task(transcription_task_pk):

    from .models import StitchTask

    task = _get_task(StitchTask, transcription_task_pk)

    if not task.is_review:
        old_pairings = None
    else:
        # Detect and delete prior pairings, if any.
        # TODO: Could this be simpler?
        old_pairings = set([
            # (left_sentence_fragment_id, right_sentence_fragment_id),
        ])
        for left_fragment in task.left.sentence_fragments.all():
            for left_sentence in left_fragment.candidate_sentences.all():
                left_sentence_fragment = None
                right_sentence_fragment = None
                for candidate in left_sentence.fragment_candidates.all():
                    if candidate.revision == task.left:
                        left_sentence_fragment = candidate
                    if candidate.revision == task.right:
                        right_sentence_fragment = candidate
                if (left_sentence_fragment is not None
                    and right_sentence_fragment is not None
                    ):
                    old_pairings.add(
                        (left_sentence_fragment.id, right_sentence_fragment.id))
                    left_sentence.remove_candidates(
                        left_sentence_fragment, right_sentence_fragment)

    # Create new pairings.
    new_pairings = set([
        # (left_sentence_fragment_id, right_sentence_fragment_id),
    ])
    # Make sure every fragment has a sentence.
    for fragment in task.left.sentence_fragments.all():
        if fragment.candidate_sentences.count() == 0:
            sentence = task.transcript.sentences.create()
            sentence.add_candidates(fragment)

    for task_pairing in task.task_pairings.all():
        new_pairings.add(
            (task_pairing.left.id, task_pairing.right.id))
        task_pairing.left.candidate_sentences.first().add_candidates(
            task_pairing.right)

    print 'old pairings', old_pairings
    print 'new pairings', new_pairings

    if not task.is_review:
        # First time.
        task.left.fragment.stitched_right = True
        if task.left.fragment.stitched_left:
            task.left.fragment.stitch()
        else:
            task.left.fragment.save()

        task.right.fragment.stitched_left = True
        if task.right.fragment.stitched_right:
            task.right.fragment.stitch()
        else:
            task.right.fragment.save()

    elif task.is_review and old_pairings == new_pairings:
        # No changes; commit sentence candidates.
        for fragment in task.left.sentence_fragments.all():
            for sentence in fragment.candidate_sentences.all():
                sentence.commit_candidates()
        # Update state of transcript fragments if fully stitched.
        if task.left.fragment.stitched_left:
            task.left.fragment.review_stitch()
        if task.right.fragment.stitched_right:
            task.right.fragment.review_stitch()

    else:
        # Changes detected; review one more time.
        pass

    task.validate()
