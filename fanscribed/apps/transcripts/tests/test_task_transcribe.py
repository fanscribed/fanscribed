from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TransactionTestCase

from ....utils import refresh
from .. import models as m


class TranscribeTaskTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@user.user', 'user')
        t = self.transcript = m.Transcript.objects.create(name='test transcript')
        t.set_length(Decimal('20.00'))

    def _submitted_task(self, fragment, text, sequence, is_review):
        tf = self.transcript.fragments.all()[fragment]
        r = tf.revisions.create(
            editor=self.user,
            sequence=sequence,
        )
        task = self.transcript.transcribetask_set.create(
            is_review=is_review,
            revision=r,
            start=tf.start,
            end=tf.end,
        )
        task.assign_to(self.user)
        task.present()
        task.text = text
        task.submit()
        task._post_submit()
        task = refresh(task)
        return task

    def test_valid_task(self):
        task = self._submitted_task(
            fragment=0,
            text='first\nsecond\n',
            sequence=1,
            is_review=False,
        )

        self.assertEqual(task.state, 'valid')
        self.assertEqual(task.revision.fragment.state, 'transcribed')

        f0, f1 = task.revision.sentence_fragments.all()
        self.assertEqual(f0.text, 'first')
        self.assertEqual(f1.text, 'second')

    def test_invalid_task(self):
        task = self._submitted_task(
            fragment=0,
            text=' ',
            sequence=1,
            is_review=False,
        )

        self.assertEqual(task.state, 'invalid')
        self.assertIsNone(task.revision)

        fragments = self.transcript.fragments.all()
        self.assertEqual(fragments[0].state, 'empty')

    def test_valid_review_with_changes(self):
        self._submitted_task(
            fragment=0,
            text='first\nsecond\n',
            sequence=1,
            is_review=False,
        )
        task = self._submitted_task(
            fragment=0,
            text='first\nsecond\nthird\n',
            sequence=2,
            is_review=True,
        )

        self.assertEqual(task.state, 'valid')
        self.assertEqual(task.revision.fragment.state, 'transcribed')

        f0, f1, f2 = task.revision.sentence_fragments.all()
        self.assertEqual(f0.text, 'first')
        self.assertEqual(f1.text, 'second')
        self.assertEqual(f2.text, 'third')

    def test_valid_review_without_changes(self):
        self._submitted_task(
            fragment=0,
            text='first\nsecond\n',
            sequence=1,
            is_review=False,
        )
        task = self._submitted_task(
            fragment=0,
            text='first\nsecond\n',
            sequence=2,
            is_review=True,
        )

        self.assertEqual(task.state, 'valid')
        self.assertEqual(task.revision.fragment.state, 'transcript_reviewed')

        f0, f1 = task.revision.sentence_fragments.all()
        self.assertEqual(f0.text, 'first')
        self.assertEqual(f1.text, 'second')

    def test_invalid_review(self):
        self._submitted_task(
            fragment=0,
            text='first\nsecond\n',
            sequence=1,
            is_review=False,
        )
        task = self._submitted_task(
            fragment=0,
            text=' ',
            sequence=2,
            is_review=True,
        )

        self.assertEqual(task.state, 'invalid')
        self.assertIsNone(task.revision)

        fragments = self.transcript.fragments.all()
        self.assertEqual(fragments[0].state, 'transcribed')
