from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
import vanilla

from ..transcripts.models import Transcript
from .models import Episode, Podcast
from .tasks import fetch_episode_raw_media


# ----------------------------------


class PodcastList(vanilla.ListView):

    model = Podcast


class PodcastDetail(vanilla.DetailView):

    model = Podcast


# ----------------------------------


class EpisodeDetail(vanilla.DetailView):

    model = Episode


class EpisodeCreateTranscript(vanilla.RedirectView):

    http_method_names = ['post']

    def get_redirect_url(self, podcast_pk, pk):
        episode = get_object_or_404(
            Episode, podcast__pk=podcast_pk, pk=pk)

        if not episode.transcript:
            # Create a transcript for this episode.
            episode.transcript = Transcript.objects.create(title=episode.title)
            episode.save()
        else:
            # Episode already has transcript.
            pass

        fetch_episode_raw_media.delay(episode.pk)

        transcript = episode.transcript
        return reverse('transcripts:detail', kwargs=dict(pk=transcript.pk))
