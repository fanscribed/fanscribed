from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse, HttpResponseServerError
from django.views.generic import View


class EmberIndexView(View):

    base_url = '/'

    def get(self, request):
        base_url = self.base_url
        while base_url.startswith('/'):
            base_url = base_url[1:]
        index_path = base_url + 'index.html'
        index_file = finders.find(index_path)
        if index_file:
            with open(index_file, 'rb') as f:
                index_content = f.read().decode('utf8')
            if settings.DEBUG:
                index_content = index_content.replace(
                    'href="assets/',
                    'href="{}{}assets/'.format(settings.STATIC_URL,
                                               self.base_url[1:]),
                )
                index_content = index_content.replace(
                    'src="assets/',
                    'src="{}{}assets/'.format(settings.STATIC_URL,
                                              self.base_url[1:]),
                )
            return HttpResponse(index_content)
        else:
            return HttpResponseServerError('index not found')
