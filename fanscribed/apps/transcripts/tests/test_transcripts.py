from django.test import TestCase

from unipath import Path

from ...media.models import MediaFile
from ...media import tests
from ..models import Transcript, TranscriptMedia

MEDIA_TESTDATA_PATH = Path(tests.__file__).parent.child('testdata')

RAW_MEDIA_PATH = MEDIA_TESTDATA_PATH.child('raw').child(
    'NA-472-2012-12-23-Final-excerpt.mp3')


class TranscriptsTestCase(TestCase):

    def test_transcript_starts_out_with_unknown_length(self):
        transcript = Transcript(name='test transcript')
        self.assertEqual(transcript.length, None)
        self.assertEqual(transcript.length_state, 'unknown')

    def test_transcriptmedia_starts_out_with_unknown_length(self):
        media_file = MediaFile.objects.create(
            data_url='file://{}'.format(RAW_MEDIA_PATH),
        )
        transcript = Transcript.objects.create(
            name='test transcript',
        )
        transcript_media = TranscriptMedia.objects.create(
            transcript=transcript,
            media_file=media_file,
            is_raw_media=True,
            is_full_length=True,
        )
        self.assertEqual(transcript_media.start, None)
        self.assertEqual(transcript_media.end, None)
        self.assertEqual(transcript_media.timecode_state, 'unknown')
