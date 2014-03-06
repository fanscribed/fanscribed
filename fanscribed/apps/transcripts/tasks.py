from celery.app import shared_task

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
    transcript.length = processed_transcript_media.end
    transcript.save()
