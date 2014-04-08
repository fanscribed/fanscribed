from hashlib import sha1
import os
import random
from shutil import move

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel
from unipath import Path

from .tasks import create_processed_transcript_media


CACHE_PATH = Path(settings.MEDIA_CACHE_PATH).absolute()
CHUNK_SIZE = 262144


def local_cache_path(fieldfile):
    """Return local cache path for this media file, fetching as needed."""

    url_hash = sha1(fieldfile.url).hexdigest()
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    path = CACHE_PATH.child(url_hash)

    # If it's already cached, use it.
    if path.exists():
        return path

    # Not cached; retrieve and store it.
    # Start out with a temp file, to avoid one process clobbering another.
    temp_path = '{}_{}'.format(path, random.randint(10000, 99999))

    fieldfile.open()
    with open(temp_path, 'wb') as out_file, fieldfile as in_file:
        chunk = in_file.read(CHUNK_SIZE)
        while chunk != '':
            out_file.write(chunk)
            chunk = in_file.read(CHUNK_SIZE)

    move(temp_path, path)
    return path


# ---------------------


class TranscriptMedia(TimeStampedModel):

    # TODO: state machine around conversion process

    transcript = models.ForeignKey('transcripts.Transcript', related_name='media')
    file = models.FileField(upload_to='transcripts', max_length=1024)
    is_processed = models.BooleanField(help_text='Is it processed media?')
    is_full_length = models.BooleanField(
        help_text='Is it the full length of media to be transcribed?')
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
