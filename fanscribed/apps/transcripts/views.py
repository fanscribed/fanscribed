from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from vanilla import DetailView, ListView, RedirectView

from .models import Transcript


# -----------------------------


class TranscriptListView(ListView):

    model = Transcript


class TranscriptDetailView(DetailView):

    model = Transcript


# -----------------------------


class TaskAssignView(RedirectView):

    http_method_names = ['post']

    def get_redirect_url(self, pk):
        transcript = get_object_or_404(Transcript, pk=pk)
        # TODO: create a task here.
        # TODO: redirect to the task instead of transcript detail.
        return reverse('transcripts:detail', kwargs=dict(pk=pk))
