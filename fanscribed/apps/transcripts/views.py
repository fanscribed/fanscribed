from vanilla import DetailView, ListView

from .models import Transcript


class TranscriptList(ListView):

    model = Transcript


class TranscriptDetail(DetailView):

    model = Transcript
