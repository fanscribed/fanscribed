from django.conf.urls import patterns, include, url
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'transcripts', views.TranscriptViewSet)


urlpatterns = patterns(
    '',

    url(r'^',
        include(router.urls)),

    url(r'^auth/',
        include('rest_framework.urls', namespace='rest_framework')),
)