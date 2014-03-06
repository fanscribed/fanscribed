from django.test import TestCase

from unipath import Path

from ...media.models import MediaFile
from ...media import tests
from ..models import Transcript, TranscriptMedia

MEDIA_TESTDATA_PATH = Path(tests.__file__).parent.child('testdata')

RAW_MEDIA_PATH = MEDIA_TESTDATA_PATH.child('raw').child(
    'NA-472-2012-12-23-Final-excerpt.mp3').absolute()


class TranscriptsTestCase(TestCase):

    def test_transcript_starts_out_with_unknown_length(self):
        transcript = Transcript(name='test transcript')
        self.assertEqual(transcript.length, None)

    def test_transcript_with_processed_media_has_length(self):
        media_file = MediaFile.objects.create(
            data_url='file://{}'.format(RAW_MEDIA_PATH),
        )
        transcript = Transcript.objects.create(
            name='test transcript',
        )
        transcript_media = TranscriptMedia.objects.create(
            transcript=transcript,
            media_file=media_file,
            is_processed=False,
            is_full_length=True,
        )
        transcript_media.create_processed()

        # Reload changed objects.
        transcript = Transcript.objects.get(pk=transcript.pk)

        # Check length.
        expected_length = 5 * 60  # 5 minutes.
        self.assertAlmostEqual(transcript.length, expected_length, delta=0.2)
