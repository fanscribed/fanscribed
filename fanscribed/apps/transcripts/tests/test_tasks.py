from fanscribed.utils import refresh

from .base import BaseTaskTestCase


class TaskTestCase(BaseTaskTestCase):

    def test_transcript_becomes_finished_when_all_phases_finished(self):
        self.setup_transcript('13.33', 2)

        self.transcribe_and_review(0, 'sentence 1')
        self.transcribe_and_review(1, 'sentence 2')
        self.stitch(0, 1, [])
        self.review_stitch(0, 1)

        def lock_and_submit(t):
            t.lock()
            t.prepare()
            t.assign_to(self.user)
            t.present()
            return self.submit(t)
        
        s0, s1 = self.transcript.sentences.all()
        
        # Set boundaries.
        
        self.assertEqual(s0.boundary_state, 'untouched')
        lock_and_submit(self.transcript.boundarytask_set.create(
            is_review=False,
            sentence=s0,
            start='1.00',
            end='2.00',
        ))
        s0 = refresh(s0)
        self.assertEqual(s0.boundary_state, 'edited')

        lock_and_submit(self.transcript.boundarytask_set.create(
            is_review=True,
            sentence=s0,
            start='1.00',
            end='2.00',
        ))
        s0 = refresh(s0)
        self.assertEqual(s0.boundary_state, 'reviewed')

        self.assertEqual(s1.boundary_state, 'untouched')
        lock_and_submit(self.transcript.boundarytask_set.create(
            is_review=False,
            sentence=s1,
            start='6.00',
            end='7.00',
        ))
        s1 = refresh(s1)
        self.assertEqual(s1.boundary_state, 'edited')

        lock_and_submit(self.transcript.boundarytask_set.create(
            is_review=True,
            sentence=s1,
            start='6.00',
            end='7.00',
        ))
        s1 = refresh(s1)
        self.assertEqual(s1.boundary_state, 'reviewed')

        # Clean.
        
        self.assertEqual(s0.clean_state, 'untouched')
        lock_and_submit(self.transcript.cleantask_set.create(
            is_review=False,
            sentence=s0,
            text=s0.text,
        ))
        s0 = refresh(s0)
        self.assertEqual(s0.clean_state, 'edited')

        lock_and_submit(self.transcript.cleantask_set.create(
            is_review=True,
            sentence=s0,
            text=s0.text,
        ))
        s0 = refresh(s0)
        self.assertEqual(s0.clean_state, 'reviewed')

        self.assertEqual(s1.clean_state, 'untouched')
        lock_and_submit(self.transcript.cleantask_set.create(
            is_review=False,
            sentence=s1,
            text=s1.text,
        ))
        s1 = refresh(s1)
        self.assertEqual(s1.clean_state, 'edited')

        lock_and_submit(self.transcript.cleantask_set.create(
            is_review=True,
            sentence=s1,
            text=s1.text,
        ))
        s1 = refresh(s1)
        self.assertEqual(s1.clean_state, 'reviewed')

        # Speaker.
        
        self.assertEqual(s0.speaker_state, 'untouched')
        lock_and_submit(self.transcript.speakertask_set.create(
            is_review=False,
            sentence=s0,
            new_name='speaker 1',
        ))
        s0 = refresh(s0)
        self.assertEqual(s0.speaker_state, 'edited')

        lock_and_submit(self.transcript.speakertask_set.create(
            is_review=True,
            sentence=s0,
            speaker=s0.latest_speaker,
        ))
        s0 = refresh(s0)
        self.assertEqual(s0.speaker_state, 'reviewed')

        self.assertEqual(s1.speaker_state, 'untouched')
        lock_and_submit(self.transcript.speakertask_set.create(
            is_review=False,
            sentence=s1,
            new_name='speaker 2',
        ))
        s1 = refresh(s1)
        self.assertEqual(s1.speaker_state, 'edited')

        self.transcript = refresh(self.transcript)
        self.assertState(self.transcript, 'unfinished')

        lock_and_submit(self.transcript.speakertask_set.create(
            is_review=True,
            sentence=s1,
            speaker=s1.latest_speaker,
        ))

        self.transcript = refresh(self.transcript)
        self.assertState(self.transcript, 'finished')
