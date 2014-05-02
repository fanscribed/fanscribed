from django.core.management.base import BaseCommand

from ...apps.podcasts.models import Podcast


class Command(BaseCommand):
    help = "Load initial data"

    def handle(self, *args, **options):
        verbose = (options['verbosity'] > 0)
        if verbose:
            self.stdout.write('Fetching all RSS feeds.\n\n')
        for podcast in Podcast.objects.all():
            self.stdout.write('- {}\n  {}\n\n'.format(
                podcast.title, podcast.rss_url))
            podcast.fetches.create().start()
