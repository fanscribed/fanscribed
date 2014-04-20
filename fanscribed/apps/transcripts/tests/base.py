from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TransactionTestCase

from fanscribed.utils import refresh

from .. import models as m


class BaseTaskTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@user.user', 'user')

    def setup_transcript(self, length=Decimal('15.00'), fragments=3):
        t = self.transcript = m.Transcript.objects.create(
            title='test transcript')
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

    def transcribe(self, fragment, text, sequence, is_review=False,
                   submit=True):
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

    def review_stitch(self, left_index, right_index, verify=None, alter=None,
                      submit=True):
        tf_left = self.tfragments[left_index]
        tf_right = self.tfragments[right_index]
        stitch = self.transcript.stitches.get(left=tf_left, right=tf_right)

        task = self.transcript.stitchtask_set.create(
            is_review=True,
            stitch=stitch,
        )
        task.lock()
        task.create_pairings_from_prior_task()
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
