# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Transcript.state'
        db.add_column(u'transcripts_transcript', 'state',
                      self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unfinished', max_length=50),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Transcript.state'
        db.delete_column(u'transcripts_transcript', 'state')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'transcripts.boundarytask': {
            'Meta': {'object_name': 'BoundaryTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptMedia']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Sentence']"}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'preparing'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.cleantask': {
            'Meta': {'object_name': 'CleanTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptMedia']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Sentence']"}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'preparing'", 'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.sentence': {
            'Meta': {'ordering': "('tf_start__start', 'tf_sequence')", 'object_name': 'Sentence'},
            'boundary_lock_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'boundary_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'untouched'", 'max_length': '50'}),
            'clean_lock_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'clean_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'untouched'", 'max_length': '50'}),
            'fragment_candidates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'candidate_sentences'", 'symmetrical': 'False', 'to': u"orm['transcripts.SentenceFragment']"}),
            'fragments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sentences'", 'symmetrical': 'False', 'to': u"orm['transcripts.SentenceFragment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_end': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'latest_speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Speaker']", 'null': 'True', 'blank': 'True'}),
            'latest_start': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'latest_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'speaker_lock_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'speaker_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'untouched'", 'max_length': '50'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'empty'", 'max_length': '50'}),
            'tf_sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tf_start': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptFragment']"}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentences'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.sentenceboundary': {
            'Meta': {'ordering': "('sequence',)", 'unique_together': "[('sentence', 'sequence')]", 'object_name': 'SentenceBoundary'},
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'boundaries'", 'to': u"orm['transcripts.Sentence']"}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        u'transcripts.sentencefragment': {
            'Meta': {'ordering': "('revision__fragment__start', 'sequence')", 'unique_together': "[('revision', 'sequence')]", 'object_name': 'SentenceFragment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentence_fragments'", 'to': u"orm['transcripts.TranscriptFragmentRevision']"}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'transcripts.sentencerevision': {
            'Meta': {'ordering': "('sequence',)", 'unique_together': "[('sentence', 'sequence')]", 'object_name': 'SentenceRevision'},
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': u"orm['transcripts.Sentence']"}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'transcripts.sentencespeaker': {
            'Meta': {'ordering': "('sequence',)", 'unique_together': "[('sentence', 'sequence')]", 'object_name': 'SentenceSpeaker'},
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'speakers'", 'to': u"orm['transcripts.Sentence']"}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Speaker']"})
        },
        u'transcripts.speaker': {
            'Meta': {'unique_together': "[('transcript', 'name')]", 'object_name': 'Speaker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'speakers'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.speakertask': {
            'Meta': {'object_name': 'SpeakerTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptMedia']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'new_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Sentence']"}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Speaker']", 'null': 'True', 'blank': 'True'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'preparing'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.stitchtask': {
            'Meta': {'object_name': 'StitchTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptMedia']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'preparing'", 'max_length': '50'}),
            'stitch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.TranscriptStitch']"}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.stitchtaskpairing': {
            'Meta': {'ordering': "('left__revision__fragment__start', 'left__sequence')", 'unique_together': "[('task', 'left')]", 'object_name': 'StitchTaskPairing'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.SentenceFragment']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.SentenceFragment']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pairings'", 'to': u"orm['transcripts.StitchTask']"})
        },
        u'transcripts.transcribetask': {
            'Meta': {'object_name': 'TranscribeTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'fragment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptFragment']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptMedia']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptFragmentRevision']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'preparing'", 'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.transcript': {
            'Meta': {'object_name': 'Transcript'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'length_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unset'", 'max_length': '50'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unfinished'", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'transcripts.transcriptfragment': {
            'Meta': {'ordering': "('start',)", 'unique_together': "[('transcript', 'start', 'end')]", 'object_name': 'TranscriptFragment'},
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lock_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'lock_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unlocked'", 'max_length': '50'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'empty'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fragments'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.transcriptfragmentrevision': {
            'Meta': {'ordering': "('sequence',)", 'unique_together': "[('fragment', 'sequence')]", 'object_name': 'TranscriptFragmentRevision'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'fragment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': u"orm['transcripts.TranscriptFragment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'transcripts.transcriptmedia': {
            'Meta': {'unique_together': "(('transcript', 'is_processed', 'is_full_length', 'start', 'end'),)", 'object_name': 'TranscriptMedia'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'download_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'end': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_full_length': ('django.db.models.fields.BooleanField', [], {}),
            'is_processed': ('django.db.models.fields.BooleanField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'start': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'empty'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'media'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.transcriptstitch': {
            'Meta': {'ordering': "('left__start',)", 'unique_together': "[('transcript', 'left')]", 'object_name': 'TranscriptStitch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'stitch_at_right'", 'unique': 'True', 'to': u"orm['transcripts.TranscriptFragment']"}),
            'lock_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'lock_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unlocked'", 'max_length': '50'}),
            'right': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'stitch_at_left'", 'unique': 'True', 'to': u"orm['transcripts.TranscriptFragment']"}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'notready'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stitches'", 'to': u"orm['transcripts.Transcript']"})
        }
    }

    complete_apps = ['transcripts']