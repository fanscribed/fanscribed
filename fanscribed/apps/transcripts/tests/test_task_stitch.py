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
        task._finish_submit()
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

    def stitch(self, left_index, right_index, pairs):
        tfr_left = self.tfragments[left_index].revisions.latest()
        tfr_right = self.tfragments[right_index].revisions.latest()
        task = self.transcript.stitchtask_set.create(
            is_review=False,
            left=tfr_left,
            right=tfr_right,
        )
        task.assign_to(self.user)
        task.present()

        sf_left = tfr_left.sentence_fragments.all()
        sf_right = tfr_right.sentence_fragments.all()
        for L, R in pairs:
            task.task_pairings.create(
                left=sf_left[L],
                right=sf_right[R],
            )
        task.submit()
        task._finish_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

    def review(self, left_index, right_index, verify=None):
        tfr_left = self.tfragments[left_index].revisions.latest()
        tfr_right = self.tfragments[right_index].revisions.latest()
        task = self.transcript.stitchtask_set.create(
            is_review=True,
            left=tfr_left,
            right=tfr_right,
        )

        task.create_pairings_from_existing_candidates()
        sf_left = tfr_left.sentence_fragments.all()
        sf_right = tfr_right.sentence_fragments.all()
        if verify is not None:
            for L, R in verify:
                task.task_pairings.get(
                    left=sf_left[L],
                    right=sf_right[R],
                )

        task.assign_to(self.user)
        task.present()
        task.submit()
        task._finish_submit()
        task = refresh(task)

        self.assertState(task, 'valid')

    def check_sentences(self, expected_sentences):
        sentence_info = [
            (
                s.state,
                [f.text for f in s.fragment_candidates.all()],
                [f.text for f in s.fragments.all()],
            )
            for s in self.transcript.sentences.all()
        ]

        print
        print 'checking'
        import pprint
        pprint.pprint(sentence_info)
        print 'expecting'
        pprint.pprint(expected_sentences)
        self.assertEqual(sentence_info, expected_sentences)

    def test_no_stitching(self):
        self._transcribe_and_review(0, 'sentence 1')
        self._transcribe_and_review(1, 'sentence 2')
        self._transcribe_and_review(2, 'sentence 3')

        self.stitch(0, 1, [])

        left = self.tfragments[0]
        self.assertState(left, 'stitched')
        self.assertEqual(left.stitched_left, True)
        self.assertEqual(left.stitched_right, True)

        right = self.tfragments[1]
        self.assertState(right, 'transcript_reviewed')
        self.assertEqual(right.stitched_left, True)
        self.assertEqual(right.stitched_right, False)

        self.check_sentences([
            (u'partial', [u'sentence 1'], []),
        ])

        self.review(0, 1, [])

        left = self.tfragments[0]
        self.assertState(left, 'stitch_reviewed')
        self.assertEqual(left.stitched_left, True)
        self.assertEqual(left.stitched_right, True)

        right = self.tfragments[1]
        self.assertState(right, 'transcript_reviewed')
        self.assertEqual(right.stitched_left, True)
        self.assertEqual(right.stitched_right, False)

        self.check_sentences([
            (u'completed', [], [u'sentence 1']),
        ])

        self.stitch(1, 2, [])

        left = self.tfragments[1]
        self.assertState(left, 'stitched')
        self.assertEqual(left.stitched_left, True)
        self.assertEqual(left.stitched_right, True)

        right = self.tfragments[2]
        self.assertState(right, 'stitched')
        self.assertEqual(right.stitched_left, True)
        self.assertEqual(right.stitched_right, True)

        self.check_sentences([
            (u'completed', [], [u'sentence 1']),
            (u'partial', [u'sentence 2'], []),
            (u'partial', [u'sentence 3'], []),
        ])

        self.review(1, 2, [])

        left = self.tfragments[1]
        self.assertState(left, 'stitch_reviewed')
        self.assertEqual(left.stitched_left, True)
        self.assertEqual(left.stitched_right, True)

        right = self.tfragments[2]
        self.assertState(right, 'stitch_reviewed')
        self.assertEqual(right.stitched_left, True)
        self.assertEqual(right.stitched_right, True)

        self.check_sentences([
            (u'completed', [], [u'sentence 1']),
            (u'completed', [], [u'sentence 2']),
            (u'completed', [], [u'sentence 3']),
        ])

    def test_simple_stitching_immediate_review(self):
        self._transcribe_and_review(0, """
            sentence 1
            sentence 2a
            """)
        self._transcribe_and_review(1, """
            sentence 2b
            sentence 3
            """)
        self._transcribe_and_review(2, """
            sentence 4
            """)

        stitch_1_pairs = [
            (1, 0),
        ]
        self.stitch(0, 1, stitch_1_pairs)  # 2a + 2b

        self.check_sentences([
            ('partial', ['sentence 1'], []),
            ('partial', ['sentence 2a', 'sentence 2b'], []),
        ])

        self.review(0, 1, stitch_1_pairs)

        self.check_sentences([
            ('completed', [], ['sentence 1']),
            ('partial', ['sentence 2b'], ['sentence 2a']),
        ])

        self.stitch(1, 2, [])

        self.check_sentences([
            ('completed', [], ['sentence 1']),
            ('partial', ['sentence 2b'], ['sentence 2a']),
            ('partial', ['sentence 3'], []),
            ('partial', ['sentence 4'], []),
        ])

        self.review(1, 2, [])

        self.check_sentences([
            ('completed', [], ['sentence 1']),
            ('completed', [], ['sentence 2a', 'sentence 2b']),
            ('completed', [], ['sentence 3']),
            ('completed', [], ['sentence 4']),
        ])

    def test_complex_stitching_interleaved_review(self):
        self._transcribe_and_review(0, """
            A
            B1
            C1
            """)
        self._transcribe_and_review(1, """
            B2
            D
            C2
            """)
        self._transcribe_and_review(2, """
            B3
            E
            """)

        stitch_1_pairs = [
            (1, 0),  # B1, B2
            (2, 2),  # C1, C2
        ]
        self.stitch(0, 1, stitch_1_pairs)  # B1 + B2, C1 + C2

        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1', u'B2'], []),
            (u'partial', [u'C1', u'C2'], []),
        ])

        self.review(0, 1, stitch_1_pairs)

        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'partial', [u'B2'], [u'B1']),
            (u'partial', [u'C2'], [u'C1']),
        ])

        stitch_2_pairs = [
            (0, 0),  # B2, B3
        ]
        self.stitch(1, 2, stitch_2_pairs)  # B2 + B3

        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'partial', [u'B2', u'B3'], [u'B1']),
            (u'partial', [u'C2'], [u'C1']),
            (u'partial', [u'D'], []),
            (u'partial', [u'B3'], []),
            (u'partial', [u'E'], []),
        ])

        self.review(1, 2, verify=stitch_2_pairs)

        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'completed', [], [u'B1', u'B2', u'B3']),
            (u'completed', [], [u'C1', u'C2']),
            (u'completed', [], [u'D']),
            (u'completed', [], [u'E']),
        ])

    def test_complex_stitching_outoforder_review(self):
        self._transcribe_and_review(0, """
            A
            B1
            C1
            """)
        self._transcribe_and_review(1, """
            B2
            D
            C2
            """)
        self._transcribe_and_review(2, """
            B3
            E
            """)

        self.stitch(1, 2, [
            (0, 0),  # B2, B3
        ])

        self.check_sentences([
            (u'partial', [u'B2', u'B3'], []),
            (u'partial', [u'D'], []),
            (u'partial', [u'C2'], []),
            (u'partial', [u'B3'], []),
            (u'partial', [u'E'], []),
        ])

        self.stitch(0, 1, [
            (1, 0),  # B1, B2
            (2, 2),  # C1, C2
        ])

        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1', u'B2'], []),
            (u'partial', [u'C1', u'C2'], []),
            (u'partial', [u'B2', u'B3'], []),
            (u'partial', [u'D'], []),
            (u'partial', [u'C2'], []),
            (u'partial', [u'B3'], []),
            (u'partial', [u'E'], []),
        ])

        self.review(1, 2)

        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1'], [u'B2', u'B3']),
            (u'partial', [u'C1'], [u'C2']),
            (u'completed', [], [u'D']),
            (u'completed', [], [u'E']),
        ])

        self.review(0, 1)

        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'completed', [], [u'B1', u'B2', u'B3']),
            (u'completed', [], [u'C1', u'C2']),
            (u'completed', [], [u'D']),
            (u'completed', [], [u'E']),
        ])
