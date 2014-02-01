from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView


urlpatterns = patterns(
    '',

    url(r'^edit/$',
        name='edit',
        view=TemplateView.as_view(template_name='profiles/edit.html'),
        ),
)
