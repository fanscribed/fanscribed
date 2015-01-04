from rest_framework import serializers

from ..apps.transcripts.models import Sentence, Speaker, Transcript


class SpeakerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Speaker
        fields = ('id', 'name')


class SentenceSerializer(serializers.ModelSerializer):

    latest_speaker = SpeakerSerializer(read_only=True)

    class Meta:
        model = Sentence
        fields = ('id', 'latest_text', 'latest_start', 'latest_speaker')


class TranscriptSerializer(serializers.HyperlinkedModelSerializer):

    sentences = SentenceSerializer(many=True, read_only=True)

    class Meta:
        model = Transcript
        fields = ('url', 'id', 'title', 'state', 'length', 'length_state', 'sentences')
