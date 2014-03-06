from django.test import TestCase

from ..models import Transcript


class TranscriptsTestCase(TestCase):

    def test_transcript_starts_out_with_length_not_determined(self):
        transcript = Transcript(name='test transcript')
        self.assertEqual(transcript.length, None)
        self.assertEqual(transcript.length_state, 'not-determined')
