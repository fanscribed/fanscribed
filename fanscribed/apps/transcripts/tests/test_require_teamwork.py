from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase

from ....utils import refresh
from .. import models as m


class RequireTeamworkTestCase(TestCase):

    def setUp(self):
        # Create users that have all transcription permissions.
        all = Group.objects.create(name='all')
        task_permissions = Permission.objects.filter(
            content_type__app_label='transcripts',
            codename__startswith='add', codename__contains='task')
        all.permissions.add(*task_permissions)
        self.users = []
        for username in 'user1', 'user2':
            user = User.objects.create_user(
                username, '{}@user.user'.format(username), 'password')
            user.groups.add(all)
            self.users.append(user)

        t = self.transcript = m.Transcript.objects.create(title='test transcript')
        t.set_length(Decimal('20.00'))

    def _submitted_transcribe_task(self, task, text):
        task.text = text
        task.submit()
        task._submit()
        task = refresh(task)
        return task

    def _settings(self):
        return self.settings(TRANSCRIPTS_REQUIRE_TEAMWORK=True)

    def test_cannot_review_own_task(self):
        t = self.transcript
        u1, u2 = self.users

        with self._settings():
            # user1 performs a task.
            task1 = m.assign_next_transcript_task(t, u1, 'transcribe')
            task1 = self._submitted_transcribe_task(task1, 'text1')

            # user1 cannot review user1's own work.
            task2 = m.assign_next_transcript_task(t, u1, 'transcribe_review')
            self.assertIsNone(task2)

            # user2 can review user1's work.
            task2b = m.assign_next_transcript_task(t, u2, 'transcribe_review')
            self.assertEqual(task1.fragment, task2b.fragment)

    def test_cannot_review_own_review(self):
        t = self.transcript
        u1, u2 = self.users

        with self._settings():
            # user1 performs a task.
            task1 = m.assign_next_transcript_task(t, u1, 'transcribe')
            task1 = self._submitted_transcribe_task(task1, 'text1')

            # user2 reviews the task and changes the text.
            task2 = m.assign_next_transcript_task(t, u2, 'transcribe_review')
            task2 = self._submitted_transcribe_task(task2, 'text2')

            # user2 cannot review user2's review.
            task3 = m.assign_next_transcript_task(t, u2, 'transcribe_review')
            self.assertIsNone(task3)

            # user1 can review user2's review.
            task3b = m.assign_next_transcript_task(t, u1, 'transcribe_review')
            self.assertEqual(task1.fragment, task3b.fragment)

    def test_can_review_own_task_after_review(self):
        t = self.transcript
        u1, u2 = self.users

        with self._settings():
            # user1 performs a task.
            task1 = m.assign_next_transcript_task(t, u1, 'transcribe')
            task1 = self._submitted_transcribe_task(task1, 'text1')

            # user2 reviews the task and changes the text.
            task2 = m.assign_next_transcript_task(t, u2, 'transcribe_review')
            task2 = self._submitted_transcribe_task(task2, 'text2')

            # user2 cannot review user2's review.
            task3 = m.assign_next_transcript_task(t, u2, 'transcribe_review')
            self.assertIsNone(task3)

            # user1 can review user2's review.
            task3b = m.assign_next_transcript_task(t, u1, 'transcribe_review')
            self.assertEqual(task1.fragment, task3b.fragment)
