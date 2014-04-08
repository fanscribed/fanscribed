import os

from celery.app import shared_task
from django.core.files import File

from . import avlib


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

    from .models import local_cache_path, TranscriptMedia

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
    raw_path = local_cache_path(raw_transcript_media.file)
    processed_media = TranscriptMedia(
        transcript=transcript,
        # file will be set below.
        is_processed=True,
        is_full_length=True,
        start=0.00,
        # end will be set below.
    )

    processed_path = os.tempnam()
    avlib.convert(raw_path, processed_path, PROCESSED_MEDIA_AVCONV_SETTINGS)

    # Find length of raw media.
    raw_length = avlib.media_length(raw_path)
    raw_transcript_media.start = 0.00
    raw_transcript_media.end = raw_length
    raw_transcript_media.save()

    # Find length of processed media, and store contents and length.
    processed_media.end = avlib.media_length(processed_path)
    with open(processed_path, 'rb') as f:
        processed_media.file.save(
            '{}/processed.mp3'.format(transcript.id), File(f))
    processed_media.save()

    # Set transcript's length based on processed media.
    transcript.set_length(processed_media.end)
