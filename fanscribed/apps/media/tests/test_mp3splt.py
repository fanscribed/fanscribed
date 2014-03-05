import os
from shutil import rmtree
from tempfile import mkdtemp

from django.test import TestCase

from unipath import Path

from ..avlib import media_length
from ..mp3splt import extract_segment


TESTDATA_PATH = Path(__file__).parent.child('testdata')

CONVERTED_MEDIA = TESTDATA_PATH.child('converted').child(
    'NA-472-2012-12-23-Final-excerpt-converted.mp3')


class Mp3spltTestCase(TestCase):

    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        rmtree(self.tempdir)

    def test_slice(self):
        dest = os.path.join(self.tempdir, 'slice.mp3')
        extract_segment(CONVERTED_MEDIA, dest, 66.6, 77.7)
        expected_length = 77.7 - 66.6
        length = float(media_length(dest))
        self.assertAlmostEqual(length, expected_length, delta=0.01)
