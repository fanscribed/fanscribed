from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.template.loader import get_template
from django.views.generic import View


class EmberIndexView(View):

    # TODO: cache the rewritten index page

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
            # Insert Rollbar script.
            rollbar_template = get_template('_rollbar.html')
            rollbar_script = rollbar_template.render(RequestContext(request))
            # Ember scripts start in body, so place rollbar at end of head.
            index_content = index_content.replace('</head>', rollbar_script + '</head>')
            # Rewrite references to assets so they point to /static
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
