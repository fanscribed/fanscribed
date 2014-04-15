from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

import vanilla

from ...utils import refresh
from . import forms as f
from . import models as m

# -----------------------------


class TranscriptListView(vanilla.ListView):

    model = m.Transcript


class TranscriptDetailView(vanilla.DetailView):

    model = m.Transcript


class TranscriptTextView(vanilla.DetailView):

    model = m.Transcript
    template_name_suffix = '_text'

    def get_context_data(self, **kwargs):
        d = super(TranscriptTextView, self).get_context_data(**kwargs)
        d['sentences'] = self.object.sentences.filter(state='completed').order_by('latest_start')
        return d


# -----------------------------


class TaskAssignView(vanilla.RedirectView):

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
                    ('boundary', False),
                    ('boundary', True),
                    ('clean', False),
                    ('clean', True),
                    ('speaker', False),
                    ('speaker', True),
                ]
            elif task_type == 'any_eager':
                L = [
                    # (task_class, is_review),
                    ('boundary', True),
                    ('clean', True),
                    ('speaker', True),
                    ('boundary', False),
                    ('clean', False),
                    ('speaker', False),
                    ('stitch', True),
                    ('stitch', False),
                    ('transcribe', True),
                    ('transcribe', False),
                ]
            else:
                L = []
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
            return None


class TaskPerformView(vanilla.UpdateView):

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

    def get_success_url(self):
        return reverse('transcripts:detail',
                       kwargs=dict(pk=self.object.transcript.id))


class TaskAudioView(vanilla.DetailView):

    def get_queryset(self):
        task_type = self.kwargs['type']
        model = m.TASK_MODEL[task_type]
        return model

    def get_object(self):
        task = super(TaskAudioView, self).get_object()
        media = task.media
        return media

    def render_to_response(self, context):
        media = context['object']
        if not media.file:
            result = media.create_file_task()
            # Wait for it before continuing.
            result.get()
            media = refresh(media)
        media.record_download()
        return HttpResponseRedirect(media.file.url)
