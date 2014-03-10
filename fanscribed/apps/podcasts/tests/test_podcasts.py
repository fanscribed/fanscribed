"""RSS fetching test cases."""

import datetime

from django.test import TestCase

from unipath import Path

from ..models import Podcast, RssFetch


TESTDATA = Path(__file__).parent.child('testdata')


class RssFetchTestCase(TestCase):

    # TODO: Fetch against self-hosted sample podcast.

    def test_fetch_state_and_timestamp(self):
        podcast = Podcast.objects.create(rss_url='http://example.com/dummy.xml')
        with open(TESTDATA.child('dtfh.xml'), 'rb') as f:
            raw = f.read()
        fetch = RssFetch.objects.create(podcast=podcast)
        fetch.load_rss(raw)
        fetch.save()
        self.assertEqual(fetch.state, 'fetched')
        self.assertIsInstance(fetch.fetched, datetime.datetime)

    def test_update_podcast_title_on_successful_fetch(self):
        filename_title_map = [
            ('dtfh.xml', 'The Duncan Trussell Family Hour'),
            ('noagenda.xml', 'No Agenda'),
            ('psychedelicsalon.xml', 'Psychedelic Salon'),
            ('twit.xml', 'This Week in Tech (MP3)'),
        ]
        for filename, expected_title in filename_title_map:
            podcast = Podcast.objects.create(
                rss_url='http://example.com/{filename}'.format(**locals()))
            with open(TESTDATA.child(filename), 'rb') as f:
                raw = f.read()
            fetch = RssFetch.objects.create(podcast=podcast)
            fetch.load_rss(raw)
            fetch.save()
            self.assertEqual(podcast.title, expected_title)
