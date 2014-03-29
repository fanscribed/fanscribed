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
            state='not_transcribed',
            lock_state='unlocked',
        ).first()

        initial_revision = fragment.revisions.create(
            sequence=1,
            editor=self.request.user,
        )

        task = m.TranscriptionTask.objects.create(
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

        task = m.TranscriptionTask.objects.create(
            transcript=transcript,
            is_review=True,
            revision=next_revision,
            start=fragment.start,
            end=fragment.end,
            text=last_revision.text,
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
