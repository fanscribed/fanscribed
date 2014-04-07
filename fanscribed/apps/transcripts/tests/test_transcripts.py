from decimal import Decimal
import os

from django.test import TestCase

from unipath import Path

from ...media.models import MediaFile
from ...media import tests
from .. import models as m

MEDIA_TESTDATA_PATH = Path(tests.__file__).parent.child('testdata')

RAW_MEDIA_PATH = MEDIA_TESTDATA_PATH.child('raw').child(
    'NA-472-2012-12-23-Final-excerpt.mp3').absolute()


class TranscriptsTestCase(TestCase):

    def test_transcript_starts_out_with_unknown_length(self):
        transcript = m.Transcript.objects.create(name='test')
        self.assertEqual(transcript.length, None)

    def test_setting_transcript_length_creates_fragments_and_stitches(self):
        t = m.Transcript.objects.create(name='test')
        t.set_length('3.33')
        f0, = t.fragments.all()
        self.assertEqual(f0.start, Decimal('0.00'))
        self.assertEqual(f0.end, Decimal('3.33'))
        self.assertEqual(t.stitches.count(), 0)

        t = m.Transcript.objects.create(name='test')
        t.set_length('7.77')
        f0, = t.fragments.all()
        self.assertEqual(f0.start, Decimal('0.00'))
        self.assertEqual(f0.end, Decimal('7.77'))
        self.assertEqual(t.stitches.count(), 0)

        t = m.Transcript.objects.create(name='test')
        t.set_length('17.77')
        f0, f1, f2 = t.fragments.all()
        self.assertEqual(f0.start, Decimal('0.00'))
        self.assertEqual(f0.end, Decimal('5.00'))
        self.assertEqual(f1.start, Decimal('5.00'))
        self.assertEqual(f1.end, Decimal('10.00'))
        self.assertEqual(f2.start, Decimal('10.00'))
        self.assertEqual(f2.end, Decimal('17.77'))
        s0, s1 = t.stitches.all()
        self.assertEqual(s0.left, f0)
        self.assertEqual(s0.right, f1)
        self.assertEqual(s0.state, 'notready')
        self.assertEqual(s1.left, f1)
        self.assertEqual(s1.right, f2)
        self.assertEqual(s1.state, 'notready')


if os.environ.get('FAST_TEST') != '1':

    class SlowTranscriptsTestCase(TestCase):

        def test_transcript_with_processed_media_has_length(self):
            media_file = MediaFile.objects.create(
                data_url='file://{}'.format(RAW_MEDIA_PATH),
            )
            transcript = m.Transcript.objects.create(
                name='test transcript',
            )
            transcript_media = m.TranscriptMedia.objects.create(
                transcript=transcript,
                media_file=media_file,
                is_processed=False,
                is_full_length=True,
            )
            transcript_media.create_processed()

            # Reload changed objects.
            transcript = m.Transcript.objects.get(pk=transcript.pk)

            # Check length.
            expected_length = 5 * 60  # 5 minutes.
            self.assertAlmostEqual(transcript.length, expected_length, delta=0.2)
