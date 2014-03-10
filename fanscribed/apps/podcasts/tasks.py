from celery.app import shared_task

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
