"""RSS fetching test cases."""

import datetime

from django.test import TestCase

from unipath import Path

from ..models import Episode, Podcast, RssFetch


TESTDATA = Path(__file__).parent.child('testdata')


class RssFetchTestCase(TestCase):

    # TODO: Fetch against self-hosted sample podcast.

    def test_fetch_state_and_timestamp(self):
        podcast = Podcast.objects.create(rss_url='http://example.com/dummy.xml')
        fetch = RssFetch.objects.create(podcast=podcast)
        fetch.load_rss(filename=TESTDATA.child('dtfh.xml'))
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
            fetch = RssFetch.objects.create(podcast=podcast)
            fetch.load_rss(filename=TESTDATA.child(filename))
            self.assertEqual(podcast.title, expected_title)

    def test_create_episodes_on_first_fetch(self):
        podcast = Podcast.objects.create(
            rss_url='http://example.com/noagenda.xml')

        fetch = RssFetch.objects.create(podcast=podcast)
        fetch.load_rss(filename=TESTDATA.child('noagenda.xml'))

        episodes = Episode.objects.filter(podcast=podcast)
        expected_count = 18
        self.assertEqual(episodes.count(), expected_count)

    def test_update_episodes_on_second_fetch(self):
        podcast = Podcast.objects.create(
            rss_url='http://example.com/noagenda.xml')

        fetch1 = RssFetch.objects.create(podcast=podcast)
        fetch1.load_rss(filename=TESTDATA.child('noagenda.xml'))
        fetch2 = RssFetch.objects.create(podcast=podcast)
        fetch2.load_rss(filename=TESTDATA.child('noagenda2.xml'))

        episodes = Episode.objects.filter(podcast=podcast)
        expected_count = 20
        self.assertEqual(episodes.count(), expected_count)
