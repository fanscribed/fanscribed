from django.test import TestCase

from ..models import MediaFile

from .base import CONVERTED_NOAGENDA_MEDIA_PATH


class MediaTestCase(TestCase):

    def test_local_cache_path_differs_from_original(self):
        media_file = MediaFile.objects.create(
            data_url='file://{}'.format(CONVERTED_NOAGENDA_MEDIA_PATH))
        # Read original file data.
        with open(CONVERTED_NOAGENDA_MEDIA_PATH, 'rb') as f:
            original_data = f.read()
        # Read cached file data.
        cache_path = media_file.local_cache_path()
        with open(cache_path, 'rb') as f:
            cached_data = f.read()
        # Make sure the path is different from original path.
        self.assertNotEqual(CONVERTED_NOAGENDA_MEDIA_PATH, cache_path)
        # Make sure contents are equal.
        self.assertEqual(original_data, cached_data)
