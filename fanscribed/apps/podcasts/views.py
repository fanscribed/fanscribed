from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
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

    def render_to_response(self, context):
        transcript = self.object.transcript
        if transcript:
            # Episode already has transcript; jump to the transcript page.
            transcript_url = reverse(
                'transcripts:detail_slug',
                kwargs=dict(pk=transcript.pk, slug=slugify(transcript.title)))
            return HttpResponseRedirect(transcript_url)
        else:
            # Show a skeletal view of the episode, w/o transcript.
            return super(EpisodeDetail, self).render_to_response(context)


class EpisodeCreateTranscript(vanilla.RedirectView):

    http_method_names = ['post']
    permanent = False

    def get_redirect_url(self, podcast_pk, pk):
        episode = get_object_or_404(
            Episode, podcast__pk=podcast_pk, pk=pk)

        if not episode.transcript:
            # Create a transcript for this episode.
            episode.transcript = Transcript.objects.create(
                title=episode.title,
                created_by=self.request.user,
            )
            episode.save()
            messages.success(self.request,
                             "Thanks! We're now getting this episode ready to transcribe.")

        else:
            # Episode already has transcript.
            pass

        fetch_episode_raw_media.delay(episode.pk)

        transcript = episode.transcript
        return reverse(
            'transcripts:detail_slug',
            kwargs=dict(pk=transcript.pk, slug=slugify(transcript.title)))
