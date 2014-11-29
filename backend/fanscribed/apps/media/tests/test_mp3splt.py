import os
from shutil import rmtree
from tempfile import mkdtemp

from django.test import TestCase

from ..avlib import media_length
from ..mp3splt import extract_segment

from .base import CONVERTED_NOAGENDA_MEDIA_PATH


class Mp3spltTestCase(TestCase):

    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        rmtree(self.tempdir)

    def test_slice(self):
        dest = os.path.join(self.tempdir, 'slice.mp3')
        extract_segment(CONVERTED_NOAGENDA_MEDIA_PATH, dest, 66.6, 77.7)
        expected_length = 77.7 - 66.6
        length = float(media_length(dest))
        self.assertAlmostEqual(length, expected_length, delta=0.01)
