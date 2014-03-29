from vanilla import DetailView, ListView

from .models import Podcast


class PodcastList(ListView):

    model = Podcast


class PodcastDetail(DetailView):

    model = Podcast
