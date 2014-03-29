from vanilla import ListView

from .models import Transcript


class TranscriptList(ListView):

    model = Transcript
