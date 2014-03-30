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

    def test_valid_task(self):
        tf = self.transcript.fragments.first()
        r = tf.revisions.create(
            editor=self.user,
            sequence=1,
        )
        task = self.transcript.transcribetask_set.create(
            is_review=False,
            revision=r,
            start=tf.start,
            end=tf.end,
        )
        task.assign_to(self.user)
        task.present()
        task.text = """
            first
            second
            """
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertEqual(task.state, 'valid')

        f0, f1 = task.revision.sentence_fragments.all()
        self.assertEqual(f0.text, 'first')
        self.assertEqual(f1.text, 'second')

    def test_invalid_task(self):
        pass

    def test_valid_review(self):
        pass

    def test_invalid_review(self):
        pass
