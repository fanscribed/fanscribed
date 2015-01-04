from rest_framework import serializers

from ..apps.transcripts.models import Transcript


class TranscriptSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Transcript
        fields = ('url', 'id', 'title', 'state', 'length', 'length_state')
