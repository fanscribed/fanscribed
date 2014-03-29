from vanilla import DetailView, ListView

from .models import Episode, Podcast


# ----------------------------------


class PodcastList(ListView):

    model = Podcast


class PodcastDetail(DetailView):

    model = Podcast


# ----------------------------------


class EpisodeDetail(DetailView):

    model = Episode
