from rest_framework import serializers

from ..apps.transcripts import models


class SpeakerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Speaker
        fields = ('id', 'name')


class SentenceSerializer(serializers.ModelSerializer):

    latest_speaker = SpeakerSerializer(read_only=True)

    class Meta:
        model = models.Sentence
        fields = ('id', 'latest_text', 'latest_start', 'latest_speaker')


class SentenceFragmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SentenceFragment
        fields = ('text',)


class TranscriptFragmentSerializer(serializers.ModelSerializer):

    latest_sentence_fragments = SentenceFragmentSerializer(many=True, read_only=True)

    class Meta:
        model = models.TranscriptFragment
        fields = ('id', 'start', 'end', 'state', 'latest_sentence_fragments')


class TranscriptSerializer(serializers.ModelSerializer):

    sentences = SentenceSerializer(many=True, read_only=True)
    fragments = TranscriptFragmentSerializer(many=True, read_only=True)

    class Meta:
        model = models.Transcript
        fields = (
            'id',
            'title',
            'state',
            'length',
            'length_state',
            'sentences',
            'fragments',
        )


class TranscriptListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Transcript
        fields = ('url', 'id', 'title', 'state', 'length', 'length_state')
