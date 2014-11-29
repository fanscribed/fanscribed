from decimal import Decimal

from .base import BaseTaskTestCase


class StitchTaskTestCase(BaseTaskTestCase):

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

        self.review_stitch(0, 1, [])
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

        self.review_stitch(1, 2, [])
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

        self.review_stitch(0, 1)

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

        self.review_stitch(1, 2)

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

        self.review_stitch(0, 1, stitch_1_pairs)

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

        self.review_stitch(1, 2, verify=stitch_2_pairs)

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

        self.review_stitch(1, 2)

        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1'], [u'B2', u'B3']),
            (u'partial', [u'C1'], [u'C2']),
            (u'partial', [], [u'D']),
            (u'partial', [], [u'E']),
        ])

        self.review_stitch(0, 1)

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
        review23 = self.review_stitch(2, 3, submit=False)
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
        review12 = self.review_stitch(1, 2, submit=False)
        review12 = self.submit(review12)
        self.check_sentences([
            (u'partial', [u'A'], []),
            (u'partial', [u'B1'], [u'B2', u'B3']),
            (u'partial', [u'C1'], [u'C2']),
            (u'partial', [], [u'D']),
            (u'partial', [], [u'E1', u'E2']),
        ])
        review01 = self.review_stitch(0, 1, submit=False)
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
        review23 = self.review_stitch(2, 3, submit=False)
        stitch01 = self.submit(stitch01)
        review01 = self.review_stitch(0, 1, submit=False)
        review23 = self.submit(review23)
        review01 = self.submit(review01)
        stitch12 = self.stitch(1, 2, [
            (0, 0),  # B2, B3
        ], submit=False)
        stitch12 = self.submit(stitch12)
        review12 = self.review_stitch(1, 2, submit=False)
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
        self.review_stitch(0, 1, alter=[])
        self.review_stitch(0, 1, alter=[(0, 0)])
        self.review_stitch(0, 1)
        self.stitch(1, 2, [(0, 0)])
        self.review_stitch(1, 2, alter=[])
        self.review_stitch(1, 2, alter=[(0, 0)])
        self.review_stitch(1, 2)

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

        task = self.stitch(0, 1, [
            (2, 0),  # [m] adam curry, john c. dvorak; [m] john c. dvorak
            (3, 1),  # it's sunday december; it's sunday december 23rd 2012
        ])

        self.transcribe_and_review(2, """
            assassination episode 472
            [m] this is no agenda
            welcome to the
        """)

        task = self.review_stitch(0, 1, verify=[(2, 0), (3, 1)])

        self.transcribe_and_review(3, """
            [m]
            welcome to the other side of the apocalypse
            coming to you from the gitmo nation lowlands
            day 17
        """)

        task = self.stitch(1, 2, [
            (0, 1),  # [m] john c. dvorak; [m] this is no agenda
            (2, 0),
            # time for your gitmo nation media assassination episode; assassination episode 472
        ])

        task = self.review_stitch(1, 2, verify=[(0, 1), (2, 0)])
