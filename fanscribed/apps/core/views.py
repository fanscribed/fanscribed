from django.views.generic import TemplateView


class CoreIndexView(TemplateView):

    template_name = 'core/index.html'
