import hashlib

from django.test import TestCase

from unipath import Path

from ..models import MediaFile


TESTDATA_PATH = Path(__file__).parent.child('testdata')

MEDIA_PATH = TESTDATA_PATH.child('converted').child(
    'NA-472-2012-12-23-Final-excerpt-converted.mp3')


class MediaTestCase(TestCase):

    def test_local_cache_path(self):
        media_file = MediaFile.objects.create(
            data_url='file://{}'.format(MEDIA_PATH))
        # Read original file data.
        with open(MEDIA_PATH, 'rb') as f:
            original_data = f.read()
        # Read cached file data.
        cached_path = media_file.local_cache_path()
        with open(cached_path, 'rb') as f:
            cached_data = f.read()
        # Make sure the path is different from original path.
        self.assertNotEqual(MEDIA_PATH, cached_path)
        # Make sure contents are equal.
        self.assertEqual(original_data, cached_data)
