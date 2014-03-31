from django.http import HttpResponse
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

        if task_type in ['any_sequential', 'any_eager']:
            if task_type == 'any_sequential':
                L = [
                    # (task_class, is_review),
                    ('transcribe', False),
                    ('transcribe', True),
                    ('stitch', False),
                    ('stitch', True),
                    ('clean', False),
                    ('clean', True),
                    ('boundary', False),
                    ('boundary', True),
                    ('speaker', False),
                    ('speaker', True),
                ]
            if task_type == 'any_eager':
                L = [
                    # (task_class, is_review),
                    ('clean', True),
                    ('boundary', True),
                    ('speaker', True),
                    ('clean', False),
                    ('boundary', False),
                    ('speaker', False),
                    ('stitch', True),
                    ('stitch', False),
                    ('transcribe', True),
                    ('transcribe', False),
                ]
            for task_type, is_review in L:
                tasks = m.TASK_MODEL[task_type].objects
                if tasks.can_create(transcript, is_review):
                    task = tasks.create_next(
                        self.request.user, transcript, is_review)
                    break
            else:
                task = None
        else:
            if task_type.endswith('_review'):
                task_type = task_type.split('_review')[0]  # Trim _review off end.
                is_review = True
            else:
                is_review = False
            task = m.TASK_MODEL[task_type].objects.create_next(
                user=self.request.user,
                transcript=transcript,
                is_review=is_review,
            )

        if task:
            task.present()
            return task.get_absolute_url()
        else:
            return HttpResponse('no tasks available')


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
