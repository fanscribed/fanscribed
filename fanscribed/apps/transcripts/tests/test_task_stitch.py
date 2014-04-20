from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TransactionTestCase

from ....utils import refresh
from .. import models as m


class StitchTaskTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@user.user', 'user')

    def setup_transcript(self, length=Decimal('15.00'), fragments=3):
        t = self.transcript = m.Transcript.objects.create(title='test transcript')
        t.set_length(length)
        self.tfragments = t.fragments.all()
        self.tstitches = t.stitches.all()
        self.assertEqual(self.tfragments.count(), fragments)

    def submit(self, task):
        task.submit()
        task._submit()
        task = refresh(task)
        self.assertState(task, 'valid')
        return task

    def transcribe(self, fragment, text, sequence, is_review=False, submit=True):
        tf = self.tfragments[fragment]
        r = tf.revisions.create(
            editor=self.user,
            sequence=sequence,
        )
        task = self.transcript.transcribetask_set.create(
            is_review=is_review,
            fragment=tf,
            revision=r,
            start=tf.start,
            end=tf.end,
        )
        task.lock()
        task.prepare()
        task.assign_to(self.user)
        task.present()
        task.text = text
        task = self.submit(task) if submit else task
        return task

    def transcribe_and_review(self, fragment, text):
        self.transcribe(fragment, text, 1, is_review=False)
        self.transcribe(fragment, text, 2, is_review=True)

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

    def stitch(self, left_index, right_index, pairs, submit=True):
        tf_left = self.tfragments[left_index]
        tf_right = self.tfragments[right_index]
        stitch = self.transcript.stitches.get(left=tf_left, right=tf_right)

        task = self.transcript.stitchtask_set.create(
            is_review=False,
            stitch=stitch,
        )
        task.lock()
        task.prepare()
        task.assign_to(self.user)
        task.present()

        sf_left = tf_left.revisions.latest().sentence_fragments.all()
        sf_right = tf_right.revisions.latest().sentence_fragments.all()
        for L, R in pairs:
            task.pairings.create(
                left=sf_left[L],
                right=sf_right[R],
            )
        task = self.submit(task) if submit else task
        return task

    def review(self, left_index, right_index, verify=None, alter=None, submit=True):
        tf_left = self.tfragments[left_index]
        tf_right = self.tfragments[right_index]
        stitch = self.transcript.stitches.get(left=tf_left, right=tf_right)

        task = self.transcript.stitchtask_set.create(
            is_review=True,
            stitch=stitch,
        )
        task.lock()
        task.create_pairings_from_existing_candidates()
        task.prepare()

        sf_left = tf_left.revisions.latest().sentence_fragments.all()
        sf_right = tf_right.revisions.latest().sentence_fragments.all()
        if verify is not None:
            for L, R in verify:
                task.pairings.get(
                    left=sf_left[L],
                    right=sf_right[R],
                )

        task.assign_to(self.user)
        task.present()

        if alter is not None:
            task.pairings.all().delete()
            for L, R in alter:
                task.pairings.create(
                    left=sf_left[L],
                    right=sf_right[R],
                )

        task = self.submit(task) if submit else task
        return task

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
        self.setup_transcript()

        self.transcribe_and_review(0, u'sentence 1')
        self.transcribe_and_review(1, u'sentence 2')
        self.transcribe_and_review(2, u'sentence 3')

        self.stitch(0, 1, [])
        stitch01 = self.tstitches[0]
        self.assertState(stitch01, 'stitched')

        self.check_sentences([
            (u'partial', [u'sentence 1'], []),
        ])

        self.review(0, 1, [])
        stitch01 = self.tstitches[0]
        self.assertState(stitch01, 'reviewed')

        self.check_sentences([
            (u'partial', [], [u'sentence 1']),
        ])

        self.stitch(1, 2, [])
        stitch12 = self.tstitches[1]
        self.assertState(stitch12, 'stitched')

        self.check_sentences([
            (u'partial', [], [u'sentence 1']),
            (u'partial', [u'sentence 2'], []),
            (u'partial', [u'sentence 3'], []),
        ])

        self.review(1, 2, [])
        stitch12 = self.tstitches[1]
        self.assertState(stitch12, 'reviewed')

        self.check_sentences([
            (u'completed', [], [u'sentence 1']),
            (u'completed', [], [u'sentence 2']),
            (u'completed', [], [u'sentence 3']),
        ])

    def test_simple_stitching_immediate_review(self):
        self.setup_transcript()

        self.transcribe_and_review(0, u"""
            sentence 1
            sentence 2a
            """)
        self.transcribe_and_review(1, u"""
            sentence 2b
            sentence 3
            """)
        self.transcribe_and_review(2, u"""
            sentence 4
            """)

        self.stitch(0, 1, [
            (1, 0),  # 2a + 2b
        ])

        self.check_sentences([
            (u'partial', [u'sentence 1'], []),
            (u'partial', [u'sentence 2a', u'sentence 2b'], []),
        ])

        self.review(0, 1)

        self.check_sentences([
            (u'partial', [], [u'sentence 1']),
            (u'partial', [], [u'sentence 2a', u'sentence 2b']),
        ])

        self.stitch(1, 2, [])

        self.check_sentences([
            (u'partial', [], [u'sentence 1']),
            (u'partial', [], [u'sentence 2a', u'sentence 2b']),
            (u'partial', [u'sentence 3'], []),
            (u'partial', [u'sentence 4'], []),
        ])

        self.review(1, 2)

        self.check_sentences([
            (u'completed', [], [u'sentence 1']),
            (u'completed', [], [u'sentence 2a', u'sentence 2b']),
            (u'completed', [], [u'sentence 3']),
            (u'completed', [], [u'sentence 4']),
        ])

    def test_complex_stitching_interleaved_review(self):
        self.setup_transcript()

        self.transcribe_and_review(0, """
            A
            B1
            C1
            """)
        self.transcribe_and_review(1, """
            B2
            D
            C2
            """)
        self.transcribe_and_review(2, """
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
            (u'partial', [], [u'A']),
            (u'partial', [], [u'B1', u'B2']),
            (u'partial', [], [u'C1', u'C2']),
        ])

        stitch_2_pairs = [
            (0, 0),  # B2, B3
        ]
        self.stitch(1, 2, stitch_2_pairs)  # B2 + B3

        self.check_sentences([
            (u'partial', [], [u'A']),
            (u'partial', [], [u'B1', u'B2']),
            (u'partial', [], [u'C1', u'C2']),
            (u'partial', [u'D'], []),
            (u'partial', [u'B2', u'B3'], []),
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
        self.setup_transcript()

        self.transcribe_and_review(0, """
            A
            B1
            C1
            """)
        self.transcribe_and_review(1, """
            B2
            D
            C2
            """)
        self.transcribe_and_review(2, """
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
            (u'partial', [u'E'], []),
        ])

        self.stitch(0, 1, [
            (1, 0),  # B1, B2
            (2, 2),  # C1, C2
        ])

        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1', u'B2', u'B3'], []),
            (u'partial', [u'C1', u'C2'], []),
            (u'partial', [u'D'], []),
            (u'partial', [u'E'], []),
        ])

        self.review(1, 2)

        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1'], [u'B2', u'B3']),
            (u'partial', [u'C1'], [u'C2']),
            (u'partial', [], [u'D']),
            (u'partial', [], [u'E']),
        ])

        self.review(0, 1)

        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'completed', [], [u'B1', u'B2', u'B3']),
            (u'completed', [], [u'C1', u'C2']),
            (u'completed', [], [u'D']),
            (u'completed', [], [u'E']),
        ])

    def test_complex_stitching_outoforder_review_overlapping_tasks_1(self):
        self.setup_transcript(Decimal('20.00'), 4)

        self.transcribe_and_review(0, """
            A
            B1
            C1
            """)
        self.transcribe_and_review(1, """
            B2
            D
            C2
            """)
        self.transcribe_and_review(2, """
            B3
            E1
            """)
        self.transcribe_and_review(3, """
            E2
            """)

        stitch01 = self.stitch(0, 1, [
            (1, 0),  # B1, B2
            (2, 2),  # C1, C2
        ], submit=False)
        stitch23 = self.stitch(2, 3, [
            (1, 0),  # E1, E2
        ], submit=False)
        stitch23 = self.submit(stitch23)
        self.check_sentences([
            (u'partial', [u'B3'], []),
            (u'partial', [u'E1', u'E2'], []),
        ])
        review23 = self.review(2, 3, submit=False)
        stitch01 = self.submit(stitch01)
        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1', u'B2'], []),
            (u'partial', [u'C1', u'C2'], []),
            (u'partial', [u'B3'], []),
            (u'partial', [u'E1', u'E2'], []),
        ])
        review23 = self.submit(review23)
        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1', u'B2'], []),
            (u'partial', [u'C1', u'C2'], []),
            (u'partial', [], [u'B3']),
            (u'partial', [], [u'E1', u'E2']),
        ])
        stitch12 = self.stitch(1, 2, [
            (0, 0),  # B2, B3
        ], submit=False)
        stitch12 = self.submit(stitch12)
        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1', u'B2', u'B3'], []),
            (u'partial', [u'C1', u'C2'], []),
            (u'partial', [u'D'], []),
            (u'partial', [], [u'B3']),
            (u'partial', [], [u'E1', u'E2']),
        ])
        review12 = self.review(1, 2, submit=False)
        review12 = self.submit(review12)
        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1'], [u'B2', u'B3']),
            (u'partial', [u'C1'], [u'C2']),
            (u'partial', [], [u'D']),
            (u'partial', [], [u'E1', u'E2']),
        ])
        review01 = self.review(0, 1, submit=False)
        review01 = self.submit(review01)
        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'completed', [], [u'B1', u'B2', u'B3']),
            (u'completed', [], [u'C1', u'C2']),
            (u'completed', [], [u'D']),
            (u'completed', [], [u'E1', u'E2']),
        ])

    def test_complex_stitching_outoforder_review_overlapping_tasks_2(self):
        self.setup_transcript(Decimal('20.00'), 4)

        self.transcribe_and_review(0, """
            A
            B1
            C1
            """)
        self.transcribe_and_review(1, """
            B2
            D
            C2
            """)
        self.transcribe_and_review(2, """
            B3
            E1
            """)
        self.transcribe_and_review(3, """
            E2
            """)

        stitch23 = self.stitch(2, 3, [
            (1, 0),  # E1, E2
        ], submit=False)
        stitch01 = self.stitch(0, 1, [
            (1, 0),  # B1, B2
            (2, 2),  # C1, C2
        ], submit=False)
        stitch23 = self.submit(stitch23)
        review23 = self.review(2, 3, submit=False)
        stitch01 = self.submit(stitch01)
        review01 = self.review(0, 1, submit=False)
        review23 = self.submit(review23)
        review01 = self.submit(review01)
        stitch12 = self.stitch(1, 2, [
            (0, 0),  # B2, B3
        ], submit=False)
        stitch12 = self.submit(stitch12)
        review12 = self.review(1, 2, submit=False)
        review12 = self.submit(review12)
        self.check_sentences([
            (u'completed', [], [u'A']),
            (u'completed', [], [u'B1', u'B2', u'B3']),
            (u'completed', [], [u'C1', u'C2']),
            (u'completed', [], [u'D']),
            (u'completed', [], [u'E1', u'E2']),
        ])

    def test_review_removes_and_readds_stitch(self):
        self.setup_transcript()

        self.transcribe_and_review(0, """
            A1
            """)
        self.transcribe_and_review(1, """
            A2
            """)
        self.transcribe_and_review(2, """
            A3
            """)

        self.stitch(0, 1, [(0, 0)])
        self.review(0, 1, alter=[])
        self.review(0, 1, alter=[(0, 0)])
        self.review(0, 1)
        self.stitch(1, 2, [(0, 0)])
        self.review(1, 2, alter=[])
        self.review(1, 2, alter=[(0, 0)])
        self.review(1, 2)

        self.check_sentences([
            (u'completed', [], [u'A1', u'A2', u'A3']),
        ])

    def test_non_review_stitch_accurately_creates_pairings(self):
        self.setup_transcript('20.00', 4)

        self.transcribe_and_review(0, """
            stellar, stellar
            :)
            [m] adam curry, john c. dvorak
            it's sunday december
        """)
        self.transcribe_and_review(1, """
            [m] john c. dvorak
            it's sunday december 23rd 2012
            time for your gitmo nation media assassination episode
        """)
        self.transcribe_and_review(2, """
            assassination episode 472
            [m] this is no agenda
            welcome to the
        """)

        task = self.stitch(0, 1, [
            (2, 0),  # [m] adam curry, john c. dvorak; [m] john c. dvorak
            (3, 1),  # it's sunday december; it's sunday december 23rd 2012
        ])
        print '---'
        for pairing in task.pairings.all():
            print pairing

        task = self.review(0, 1, verify=[(2, 0), (3, 1)])
        print '--- review'
        for pairing in task.pairings.all():
            print pairing

        task = self.stitch(1, 2, [
            (0, 1),  # [m] john c. dvorak; [m] this is no agenda
            (2, 0),  # time for your gitmo nation media assassination episode; assassination episode 472
        ])
        print '---'
        for pairing in task.pairings.all():
            print pairing

        self.transcribe_and_review(3, """
            [m]
            welcome to the other side of the apocalypse
            coming to you from the gitmo nation lowlands
            day 17
        """)

        task = self.review(1, 2, verify=[(0, 1), (2, 0)])
        print '--- review'
        for pairing in task.pairings.all():
            print pairing
