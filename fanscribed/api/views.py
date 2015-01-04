from rest_framework import viewsets

from ..apps.transcripts.models import (
    Transcript,
)

from .serializers import TranscriptSerializer


class TranscriptViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
