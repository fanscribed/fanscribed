from decimal import Decimal

from django.test import TestCase

from ..models import Transcript


class TranscribeTaskTestCase(TestCase):

    def setUp(self):
        t = self.transcript = Transcript.objects.create(name='test transcript')
        t.set_length(Decimal('30.00'))

    def test_valid_task(self):
        pass

    def test_invalid_task(self):
        pass

    def test_valid_review(self):
        pass

    def test_invalid_review(self):
        pass
