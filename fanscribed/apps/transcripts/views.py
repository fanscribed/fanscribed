from django.shortcuts import get_object_or_404

from vanilla import DetailView, UpdateView, ListView, RedirectView

from . import forms as f
from . import models as m


# -----------------------------


class TranscriptListView(ListView):

    model = m.Transcript


class TranscriptDetailView(DetailView):

    model = m.Transcript


# -----------------------------


class TaskAssignView(RedirectView):

    http_method_names = ['post']

    def get_redirect_url(self, pk):
        transcript = get_object_or_404(m.Transcript, pk=pk)

        task_type = self.request.POST['type']
        task_create_method_name = 'task_create_{}'.format(task_type)
        task_create_method = getattr(self, task_create_method_name)

        task = task_create_method(transcript)
        task.assign_to(self.request.user)
        task.present()
        return task.get_absolute_url()

    def task_create_transcribe(self, transcript):

        # Find first fragment not yet transcribed.
        fragment = transcript.fragments.filter(
            state='empty',
            lock_state='unlocked',
        ).first()

        initial_revision = fragment.revisions.create(
            sequence=1,
            editor=self.request.user,
        )

        task = m.TranscribeTask.objects.create(
            transcript=transcript,
            is_review=False,
            revision=initial_revision,
            start=fragment.start,
            end=fragment.end,
        )

        return task

    def task_create_transcribe_review(self, transcript):

        # Find first fragment transcribed and not reviewed.
        fragment = transcript.fragments.filter(
            state='transcribed',
            lock_state='unlocked',
        ).first()

        last_revision = fragment.revisions.latest()

        next_revision = fragment.revisions.create(
            sequence=last_revision.sequence + 1,
            editor=self.request.user,
        )

        task = m.TranscribeTask.objects.create(
            transcript=transcript,
            is_review=True,
            revision=next_revision,
            start=fragment.start,
            end=fragment.end,
            text=last_revision.text,
        )

        return task

    def task_create_stitch(self, transcript):

        # Find first two adjacent fragments not yet stitched together.
        unstitched_fragments = transcript.fragments.filter(
            state='transcript_reviewed',
            lock_state='unlocked',
            stitched_right=False,
        )
        if unstitched_fragments.count() == 0:
            raise Exception('No more unstitched fragments.')
        for left in unstitched_fragments:
            try:
                right = transcript.fragments.get(
                    start=left.end,
                    state='transcript_reviewed',
                    stitched_left=False,
                    lock_state='unlocked',
                )
            except m.TranscriptFragment.DoesNotExist:
                # No neighbor; keep trying.
                pass
            else:
                # Found our match.
                break
        else:
            # No match found.
            raise Exception('No unlocked stitches available.')

        task = m.StitchTask.objects.create(
            transcript=transcript,
            is_review=False,
            left=left.revisions.latest(),
            right=right.revisions.latest(),
        )

        return task

    def task_create_stitch_review(self, transcript):

        # Find first two adjacent fragments already stitched together.
        stitched_fragments = transcript.fragments.filter(
            state__in=['transcript_reviewed', 'stitched'],
            lock_state='unlocked',
            stitched_right=True,
        )
        if stitched_fragments.count() == 0:
            raise Exception('No more stitched fragments to review.')
        for left in stitched_fragments:
            try:
                right = transcript.fragments.get(
                    start=left.end,
                    state__in=['transcript_reviewed', 'stitched'],
                    stitched_left=True,
                    lock_state='unlocked',
                )
            except m.TranscriptFragment.DoesNotExist:
                # No neighbor; keep trying.
                pass
            else:
                # Found our match.
                break
        else:
            # No match found.
            raise Exception('No unlocked stitches available to review.')

        task = m.StitchTask.objects.create(
            transcript=transcript,
            is_review=True,
            left=left.revisions.latest(),
            right=right.revisions.latest(),
        )

        # Create StitchTaskPairings based on existing candidate pairings.
        for left_fragment in task.left.sentence_fragments.all():
            for left_sentence in left_fragment.candidate_sentences.all():
                left_sentence_fragment = None
                right_sentence_fragment = None
                for candidate in left_sentence.fragment_candidates.all():
                    if candidate.revision == task.left:
                        left_sentence_fragment = candidate
                    if candidate.revision == task.right:
                        right_sentence_fragment = candidate
                if (left_sentence_fragment is not None
                    and right_sentence_fragment is not None
                    ):
                    # print left_sentence_fragment.text, right_sentence_fragment.text
                    task.task_pairings.create(
                        left=left_sentence_fragment,
                        right=right_sentence_fragment,
                    )

        return task


class TaskPerformView(UpdateView):

    context_object_name = 'task'

    def get_form_class(self):
        task_type = self.kwargs['type']
        form_class = f.TASK_FORM[task_type]
        return form_class

    def get_queryset(self):
        task_type = self.kwargs['type']
        model = m.TASK_MODEL[task_type]
        return model

    def get_template_names(self):
        task_type = self.kwargs['type']
        return [
            'transcripts/task_{}_detail.html'.format(task_type),
        ]
