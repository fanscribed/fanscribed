from django.contrib.sitemaps import Sitemap

from .apps.podcasts.models import Podcast, Episode
from .apps.transcripts.models import Transcript


class PodcastSitemap(Sitemap):

    def items(self):
        return Podcast.objects.all()


class EpisodeSitemap(Sitemap):

    def items(self):
        return Episode.objects.all()


class TranscriptSitemap(Sitemap):

    def items(self):
        return Transcript.objects.all()


SITEMAPS = {
    'podcasts': PodcastSitemap,
    'episodes': EpisodeSitemap,
    'transcripts': TranscriptSitemap,
}
