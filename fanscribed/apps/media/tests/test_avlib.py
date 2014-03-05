from django.test import TestCase

from unipath import Path

from ..avlib import media_length


TESTDATA_PATH = Path(__file__).parent.child('testdata')

CONVERTED_MEDIA = TESTDATA_PATH.child('converted').child(
    'NA-472-2012-12-23-Final-excerpt-converted.mp3')


class AvlibTestCase(TestCase):

    def test_media_length(self):
        expected_length = 5 * 60  # 5 minutes.
        length = float(media_length(CONVERTED_MEDIA))
        self.assertAlmostEqual(length, expected_length, delta=0.2)
