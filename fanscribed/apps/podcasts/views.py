from vanilla import ListView

from .models import Podcast


class PodcastList(ListView):

    model = Podcast
    template_name = 'podcasts/list.html'
