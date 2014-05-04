from decimal import Decimal

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

import vanilla

from ...utils import refresh
from . import forms as f
from . import models as m

# -----------------------------


class TranscriptListView(vanilla.ListView):

    model = m.Transcript

    def get_queryset(self):
        return self.model.objects.unfinished()


class TranscriptDetailView(vanilla.DetailView):

    model = m.Transcript


# -----------------------------


class AssignsTasks(object):

    # noinspection PyUnresolvedReferences
    def assigned_task_url(self, transcript, requested_task_type):

        user = self.request.user

        task = m.existing_transcript_task(transcript, user)
        if task is not None:
            messages.info(self.request,
                          "We found a task you haven't completed.")
        else:
            task = m.assign_next_transcript_task(
                transcript, user, requested_task_type)

        if task:
            return task.get_absolute_url() + '?t=' + requested_task_type
        else:
            messages.info(self.request,
                          'For this transcript, there are no tasks for you at this time.')
            return reverse(
                'transcripts:detail_slug',
                kwargs=dict(pk=transcript.pk, slug=slugify(transcript.title)))


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
                'transcripts:detail_slug',
                kwargs=dict(pk=task.transcript.id,
                            slug=slugify(task.transcript.title)))
            messages.info(self.request, "Exited the task without saving.")
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
        if self.request.user.is_staff:
            return model
        else:
            assigned_to_user = model.objects.filter(assignee=self.request.user)
            return assigned_to_user

    def get_template_names(self):
        task_type = self.kwargs['type']
        return [
            'transcripts/task_{}_detail.html'.format(task_type),
        ]

    def get_success_url(self):
        exiting = (self.request.POST.get('exit') == '1')
        if exiting:
            # Go back to the transcript detail page.
            messages.success(self.request,
                             "Thank you for your work!")
            return reverse(
                'transcripts:detail_slug',
                kwargs=dict(pk=self.object.transcript.id,
                            slug=slugify(self.object.transcript.title)))
        else:
            # Give them the next task for the given task type.
            messages.success(self.request,
                             "Thank you for your work! Here's another task.")
            default_task_type = 'any_{}'.format(
                self.request.user.profile.task_order)
            requested_task_type = self.request.GET.get('t', default_task_type)
            return self.assigned_task_url(
                self.object.transcript, requested_task_type)


class TaskAudioView(vanilla.DetailView):

    def get_queryset(self):
        task_type = self.kwargs['type']
        model = m.TASK_MODEL[task_type]
        if self.request.user.is_staff:
            return model
        else:
            assigned_to_user = model.objects.filter(assignee=self.request.user)
            return assigned_to_user

    def render_to_response(self, context):
        task = context['object']

        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        if start and end:
            start, end = Decimal(start), Decimal(end)
            start = max(start, Decimal(0))
            end = min(end, task.transcript.length)

            # Get or create a new media object.
            media, created = task.transcript.media.get_or_create(
                is_processed=True,
                is_full_length=False,
                start=start,
                end=end,
            )
            task.media = media

            # Update the task in case the page is reloaded.
            task.start = start
            task.end = end

            task.save()
        else:
            media = task.media

        if not media.file:
            result = media.create_file_task()
            # Wait for it before continuing.
            result.get()
            media = refresh(media)

        media.record_download()
        return HttpResponseRedirect(media.file.url)
