from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

import vanilla
from fanscribed.locks import LockException

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


class AssignsTasks(object):

    # noinspection PyUnresolvedReferences
    def assigned_task_url(self, transcript, requested_task_type):

        # Determine which order to search for available tasks.
        if requested_task_type == 'any_sequential':
            # Sequential moves through the pipeline in one stage at a time.
            L = [
                # (task_type, is_review),
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
        elif requested_task_type == 'any_eager':
            # Eager switches you to a new task type as soon as one is available.
            L = [
                # (task_type, is_review),
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
            # An individual task type was selected.
            if requested_task_type.endswith('_review'):
                task_type = requested_task_type.split('_review')[
                    0]  # Remove '_review'.
                is_review = True
            else:
                is_review = False
            L = [(requested_task_type, is_review)]

        # Try to create the next available type of task.
        task = None
        for task_type, is_review in L:
            # Does the user have permission?
            perm_name = 'transcripts.add_{}task{}'.format(
                task_type,
                '_review' if is_review else '',
            )
            if not self.request.user.has_perm(perm_name):
                continue
            # User has permission, so try to create this type of task.
            tasks = m.TASK_MODEL[task_type].objects
            if tasks.can_create(transcript, is_review):
                # Try to get this kind of task,
                # ignoring lock failures up to 5 times.
                for x in xrange(5):
                    try:
                        task = tasks.create_next(
                            self.request.user, transcript, is_review)
                    except LockException:
                        # Try again.
                        continue
                    else:
                        break
                if task:
                    break

        if task:
            task.present()
            return task.get_absolute_url() + '?t=' + requested_task_type
        else:
            messages.info(self.request,
                          'There are no tasks for you on this transcript at this time.')
            return reverse('transcript:detail', kwargs=dict(pk=transcript.pk))


class TaskAssignView(vanilla.RedirectView, AssignsTasks):

    http_method_names = ['post']

    def get_redirect_url(self, pk, *args, **kwargs):
        transcript = get_object_or_404(m.Transcript, pk=pk)
        requested_task_type = self.request.POST['type']
        return self.assigned_task_url(transcript, requested_task_type)


class TaskPerformView(vanilla.UpdateView, AssignsTasks):

    context_object_name = 'task'

    def post(self, request, *args, **kwargs):
        canceling = (request.POST.get('cancel') == '1')
        if canceling:
            # Cancel the task.
            task = self.get_object()
            task.cancel()
            # Redirect to transcript detail.
            transcript_detail_url = reverse(
                'transcripts:detail', kwargs=dict(pk=task.transcript.id))
            return HttpResponseRedirect(transcript_detail_url)
        else:
            # Normal form processing.
            return super(TaskPerformView, self).post(request, *args, **kwargs)

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
        exiting = (self.request.POST.get('exit') == '1')
        if exiting:
            # Go back to the transcript detail page.
            return reverse('transcripts:detail',
                           kwargs=dict(pk=self.object.transcript.id))
        else:
            # Give them the next task for the given task type.
            default_task_type = 'any_sequential'
            requested_task_type = self.request.GET.get('t', default_task_type)
            return self.assigned_task_url(
                self.object.transcript, requested_task_type)


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
