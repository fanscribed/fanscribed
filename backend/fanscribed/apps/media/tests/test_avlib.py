from django.test import TestCase

from ..avlib import media_length

from .base import CONVERTED_NOAGENDA_MEDIA_PATH


class AvlibTestCase(TestCase):

    def test_media_length(self):
        expected_length = 5 * 60  # 5 minutes.
        length = float(media_length(CONVERTED_NOAGENDA_MEDIA_PATH))
        self.assertAlmostEqual(length, expected_length, delta=0.2)
