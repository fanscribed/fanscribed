import os
from uuid import uuid4

from celery.app import shared_task
from django.core.files import File
import requests


@shared_task
def fetch_rss(rss_fetch_pk):

    from .models import RssFetch

    rss_fetch = RssFetch.objects.get(pk=rss_fetch_pk)
    response = requests.get(rss_fetch.podcast.rss_url)
    if response.ok:
        rss_fetch.finish(response.content)
    else:
        rss_fetch.fail()


@shared_task
def fetch_episode_raw_media(episode_pk):

    from ..transcripts.models import TranscriptMedia
    from .models import Episode

    episode = Episode.objects.get(pk=episode_pk)
    transcript = episode.transcript

    media = TranscriptMedia(
        transcript=transcript,
        # file will be set below
        is_processed=False,
        is_full_length=True,
    )

    # Stream MP3, then save it.
    uuid = uuid4().hex
    raw_path = '{transcript.id}_raw_{uuid}.mp3'.format(**locals())
    response = requests.get(episode.media_url, stream=True)
    raw_file = os.tmpfile()
    for chunk in response.iter_content(262144):
        raw_file.write(chunk)
    raw_file.seek(0)

    print 'Saving {episode.media_url} to {raw_path}'.format(**locals())
    media.file.save(raw_path, File(raw_file))
    raw_file.close()

    # Now process it into our normalized format.
    media.create_processed_task()
