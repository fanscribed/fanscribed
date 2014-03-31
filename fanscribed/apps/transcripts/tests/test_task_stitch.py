from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TransactionTestCase

from ....utils import refresh
from .. import models as m


class StitchTaskTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@user.user', 'user')
        t = self.transcript = m.Transcript.objects.create(name='test transcript')
        t.set_length(Decimal('15.00'))
        self.tfragments = t.fragments.all()
        self.assertEqual(self.tfragments.count(), 3)

    def _transcribe(self, fragment, text, sequence, is_review=False):
        tf = self.tfragments[fragment]
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

    def _transcribe_and_review(self, fragment, text):
        self._transcribe(fragment, text, 1, is_review=False)
        self._transcribe(fragment, text, 2, is_review=True)

    def assertSentenceHasCandidates(self, sentence, fragments):
        self.assertEqual(
            fragments,
            [fragment.text for fragment in sentence.fragment_candidates.all()],
        )

    def assertSentenceHasFragments(self, sentence, fragments):
        self.assertEqual(
            fragments,
            [fragment.text for fragment in sentence.fragments.all()],
        )

    def assertState(self, obj, state):
        self.assertEqual(obj.state, state)

    def test_no_stitching(self):
        self._transcribe_and_review(0, 'sentence 1')
        self._transcribe_and_review(1, 'sentence 2')

        # TODO: extend with sentence 3

        # Initial task.

        task = self.transcript.stitchtask_set.create(
            is_review=False,
            left=self.tfragments[0].revisions.latest(),
            right=self.tfragments[1].revisions.latest(),
        )
        task.assign_to(self.user)
        task.present()
        # Perform no pairing, just submit.
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

        # Check transcript fragments.

        left = self.tfragments[0]
        self.assertState(left, 'stitched')
        self.assertEqual(left.stitched_left, True)
        self.assertEqual(left.stitched_right, True)

        right = self.tfragments[1]
        self.assertState(right, 'transcript_reviewed')
        self.assertEqual(right.stitched_left, True)
        self.assertEqual(right.stitched_right, False)

        # Check sentences and sentence fragments.

        sentences = self.transcript.sentences.all()
        self.assertEqual(sentences.count(), 1)

        sentence = sentences[0]
        self.assertState(sentence, 'partial')
        self.assertSentenceHasCandidates(sentence, ['sentence 1'])
        self.assertSentenceHasFragments(sentence, [])

        # Review task.

        task = self.transcript.stitchtask_set.create(
            is_review=True,
            left=self.tfragments[0].revisions.latest(),
            right=self.tfragments[1].revisions.latest(),
        )
        task.create_pairings_from_existing_candidates()
        task.assign_to(self.user)
        task.present()
        # Perform no pairing changes, just submit.
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

        # Check transcript fragments.

        left = self.tfragments[0]
        self.assertState(left, 'stitch_reviewed')
        self.assertEqual(left.stitched_left, True)
        self.assertEqual(left.stitched_right, True)

        right = self.tfragments[1]
        self.assertState(right, 'transcript_reviewed')
        self.assertEqual(right.stitched_left, True)
        self.assertEqual(right.stitched_right, False)

        # Check sentences and sentence fragments.

        self.assertEqual(sentences.count(), 1)

        sentence = sentences[0]
        self.assertState(sentence, 'completed')
        self.assertSentenceHasCandidates(sentence, [])
        self.assertSentenceHasFragments(sentence, ['sentence 1'])

    def test_simple_stitching_immediate_review(self):
        self._transcribe_and_review(0, 'sentence 1\nsentence 2a')
        self._transcribe_and_review(1, 'sentence 2b\nsentence 3')
        self._transcribe_and_review(2, 'sentence 4')

        # -------------------------

        # Stitch task #1.

        tfr_left = self.tfragments[0].revisions.latest()
        tfr_right = self.tfragments[1].revisions.latest()
        task = self.transcript.stitchtask_set.create(
            is_review=False,
            left=tfr_left,
            right=tfr_right,
        )
        task.assign_to(self.user)
        task.present()
        task.task_pairings.create(
            left=tfr_left.sentence_fragments.all()[1],    # sentence 2a
            right=tfr_right.sentence_fragments.all()[0],  # sentence 2b
        )
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

        # Check transcript fragments.

        tfr_left = self.tfragments[0]
        self.assertState(tfr_left, 'stitched')
        self.assertEqual(tfr_left.stitched_left, True)
        self.assertEqual(tfr_left.stitched_right, True)

        tfr_right = self.tfragments[1]
        self.assertState(tfr_right, 'transcript_reviewed')
        self.assertEqual(tfr_right.stitched_left, True)
        self.assertEqual(tfr_right.stitched_right, False)

        # Check sentences and sentence fragments.

        sentences = self.transcript.sentences.all()
        self.assertEqual(sentences.count(), 2)

        sentence = sentences[0]
        self.assertState(sentence, 'partial')
        self.assertSentenceHasCandidates(sentence, ['sentence 1'])
        self.assertSentenceHasFragments(sentence, [])

        sentence = sentences[1]
        self.assertState(sentence, 'partial')
        self.assertSentenceHasCandidates(
            sentence, ['sentence 2a', 'sentence 2b'])
        self.assertSentenceHasFragments(sentence, [])

        # -------------------------

        # Review task #1.

        task = self.transcript.stitchtask_set.create(
            is_review=True,
            left=self.tfragments[0].revisions.latest(),
            right=self.tfragments[1].revisions.latest(),
        )
        task.create_pairings_from_existing_candidates()
        task.assign_to(self.user)
        task.present()
        # Perform no pairing changes, just submit.
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

        # Check transcript fragments.

        tfr_left = self.tfragments[0]
        self.assertState(tfr_left, 'stitch_reviewed')
        self.assertEqual(tfr_left.stitched_left, True)
        self.assertEqual(tfr_left.stitched_right, True)

        tfr_right = self.tfragments[1]
        self.assertState(tfr_right, 'transcript_reviewed')
        self.assertEqual(tfr_right.stitched_left, True)
        self.assertEqual(tfr_right.stitched_right, False)

        # Check sentences and sentence fragments.

        self.assertEqual(sentences.count(), 2)

        sentence = sentences[0]
        self.assertState(sentence, 'completed')
        self.assertSentenceHasCandidates(sentence, [])
        self.assertSentenceHasFragments(sentence, ['sentence 1'])

        sentence = sentences[1]
        self.assertState(sentence, 'partial')
        self.assertSentenceHasCandidates(sentence, ['sentence 2b'])
        self.assertSentenceHasFragments(sentence, ['sentence 2a'])

        # -------------------------

        # Stitch task #2.

        tfr_left = self.tfragments[1].revisions.latest()
        tfr_right = self.tfragments[2].revisions.latest()
        task = self.transcript.stitchtask_set.create(
            is_review=False,
            left=tfr_left,
            right=tfr_right,
        )
        task.assign_to(self.user)
        task.present()
        # No pairings.
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

        # Check transcript fragments.

        tfr_left = self.tfragments[1]
        self.assertState(tfr_left, 'stitched')
        self.assertEqual(tfr_left.stitched_left, True)
        self.assertEqual(tfr_left.stitched_right, True)

        tfr_right = self.tfragments[2]
        self.assertState(tfr_right, 'stitched')
        self.assertEqual(tfr_right.stitched_left, True)
        self.assertEqual(tfr_right.stitched_right, True)  # end of transcript

        # Check sentences and sentence fragments.

        sentences = self.transcript.sentences.all()
        self.assertEqual(sentences.count(), 3)

        sentence = sentences[0]
        self.assertState(sentence, 'completed')
        self.assertSentenceHasCandidates(sentence, [])
        self.assertSentenceHasFragments(sentence, ['sentence 1'])

        sentence = sentences[1]
        self.assertState(sentence, 'partial')
        self.assertSentenceHasCandidates(sentence, ['sentence 2b'])
        self.assertSentenceHasFragments(sentence, ['sentence 2a'])

        sentence = sentences[2]
        self.assertState(sentence, 'partial')
        self.assertSentenceHasCandidates(sentence, ['sentence 3'])
        self.assertSentenceHasFragments(sentence, [])

        # -------------------------

        # Review task #2.

        task = self.transcript.stitchtask_set.create(
            is_review=True,
            left=self.tfragments[1].revisions.latest(),
            right=self.tfragments[2].revisions.latest(),
        )
        task.create_pairings_from_existing_candidates()
        task.assign_to(self.user)
        task.present()
        # Perform no pairing changes, just submit.
        task.submit()
        task._post_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

        # Check transcript fragments.

        tfr_left = self.tfragments[1]
        self.assertState(tfr_left, 'stitch_reviewed')
        self.assertEqual(tfr_left.stitched_left, True)
        self.assertEqual(tfr_left.stitched_right, True)

        tfr_right = self.tfragments[2]
        self.assertState(tfr_right, 'stitch_reviewed')
        self.assertEqual(tfr_right.stitched_left, True)
        self.assertEqual(tfr_right.stitched_right, True)

        # Check sentences and sentence fragments.

        sentences = self.transcript.sentences.all()
        self.assertEqual(sentences.count(), 3)

        sentence = sentences[0]
        self.assertState(sentence, 'completed')
        self.assertSentenceHasCandidates(sentence, [])
        self.assertSentenceHasFragments(sentence, ['sentence 1'])

        sentence = sentences[1]
        self.assertState(sentence, 'completed')
        self.assertSentenceHasCandidates(sentence, [])
        self.assertSentenceHasFragments(sentence, ['sentence 2a', 'sentence 2b'])

        sentence = sentences[2]
        self.assertState(sentence, 'completed')
        self.assertSentenceHasCandidates(sentence, [])
        self.assertSentenceHasFragments(sentence, ['sentence 3'])
