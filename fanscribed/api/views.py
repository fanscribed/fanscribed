from rest_framework import viewsets

from ..apps.transcripts.models import (
    Transcript,
)

from .serializers import TranscriptSerializer, TranscriptListSerializer


class TranscriptViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer

    def list(self, request, *args, **kwargs):
        self.serializer_class = TranscriptListSerializer
        return super(TranscriptViewSet, self).list(request, *args, **kwargs)

