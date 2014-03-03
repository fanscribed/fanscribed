from django.test import TestCase

from unipath import Path

from .models import Podcast, RssFetch


TESTDATA = Path(__file__).parent.child('testdata')


class RssFetchTestCase(TestCase):

    def test_dtfh(self):
        podcast = Podcast.objects.create(rss_url='http://example.com/dummy.xml')
        with open(TESTDATA.child('dtfh.xml'), 'rb') as f:
            raw = f.read()
        fetch = RssFetch.objects.create(podcast=podcast)
        fetch.load_rss(raw)
        fetch.save()
        self.assertEqual(fetch.state, 'fetched')
        self.assertIsNotNone(fetch.fetched)
