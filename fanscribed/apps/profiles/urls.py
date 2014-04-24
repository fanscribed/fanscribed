from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from . import views as v


urlpatterns = patterns(
    '',

    url(r'^edit/$',
        name='edit',
        view=v.ProfileUpdateView.as_view()),
)
