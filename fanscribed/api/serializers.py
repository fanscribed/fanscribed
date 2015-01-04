from rest_framework import serializers

from ..apps.transcripts.models import Transcript


class TranscriptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transcript
        fields = ('id', 'title', 'state', 'length', 'length_state')
