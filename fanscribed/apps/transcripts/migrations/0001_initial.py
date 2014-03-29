# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SentenceFragment'
        db.create_table(u'transcripts_sentencefragment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sentence_fragments', to=orm['transcripts.TranscriptFragmentRevision'])),
            ('sequence', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'transcripts', ['SentenceFragment'])

        # Adding unique constraint on 'SentenceFragment', fields ['revision', 'sequence']
        db.create_unique(u'transcripts_sentencefragment', ['revision_id', 'sequence'])

        # Adding model 'TranscriptionTask'
        db.create_table(u'transcripts_transcriptiontask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['transcripts.Transcript'])),
            ('is_review', self.gf('django.db.models.fields.BooleanField')()),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unassigned', max_length=50)),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transcription_tasks', null=True, to=orm['auth.User'])),
            ('revision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.TranscriptFragmentRevision'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('end', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'transcripts', ['TranscriptionTask'])

        # Adding model 'Transcript'
        db.create_table(u'transcripts_transcript', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('length', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
            ('length_state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unset', max_length=50)),
        ))
        db.send_create_signal(u'transcripts', ['Transcript'])

        # Adding model 'TranscriptFragment'
        db.create_table(u'transcripts_transcriptfragment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fragments', to=orm['transcripts.Transcript'])),
            ('start', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('end', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='not_transcribed', max_length=50)),
            ('locked_state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unlocked', max_length=50)),
        ))
        db.send_create_signal(u'transcripts', ['TranscriptFragment'])

        # Adding unique constraint on 'TranscriptFragment', fields ['transcript', 'start', 'end']
        db.create_unique(u'transcripts_transcriptfragment', ['transcript_id', 'start', 'end'])

        # Adding model 'TranscriptFragmentRevision'
        db.create_table(u'transcripts_transcriptfragmentrevision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('fragment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['transcripts.TranscriptFragment'])),
            ('sequence', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('editor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='editing', max_length=50)),
        ))
        db.send_create_signal(u'transcripts', ['TranscriptFragmentRevision'])

        # Adding unique constraint on 'TranscriptFragmentRevision', fields ['fragment', 'sequence']
        db.create_unique(u'transcripts_transcriptfragmentrevision', ['fragment_id', 'sequence'])

        # Adding model 'TranscriptMedia'
        db.create_table(u'transcripts_transcriptmedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.Transcript'])),
            ('media_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['media.MediaFile'])),
            ('is_processed', self.gf('django.db.models.fields.BooleanField')()),
            ('is_full_length', self.gf('django.db.models.fields.BooleanField')()),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('start', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
            ('end', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'transcripts', ['TranscriptMedia'])

        # Adding unique constraint on 'TranscriptMedia', fields ['transcript', 'is_processed', 'is_full_length', 'start', 'end']
        db.create_unique(u'transcripts_transcriptmedia', ['transcript_id', 'is_processed', 'is_full_length', 'start', 'end'])


    def backwards(self, orm):
        # Removing unique constraint on 'TranscriptMedia', fields ['transcript', 'is_processed', 'is_full_length', 'start', 'end']
        db.delete_unique(u'transcripts_transcriptmedia', ['transcript_id', 'is_processed', 'is_full_length', 'start', 'end'])

        # Removing unique constraint on 'TranscriptFragmentRevision', fields ['fragment', 'sequence']
        db.delete_unique(u'transcripts_transcriptfragmentrevision', ['fragment_id', 'sequence'])

        # Removing unique constraint on 'TranscriptFragment', fields ['transcript', 'start', 'end']
        db.delete_unique(u'transcripts_transcriptfragment', ['transcript_id', 'start', 'end'])

        # Removing unique constraint on 'SentenceFragment', fields ['revision', 'sequence']
        db.delete_unique(u'transcripts_sentencefragment', ['revision_id', 'sequence'])

        # Deleting model 'SentenceFragment'
        db.delete_table(u'transcripts_sentencefragment')

        # Deleting model 'TranscriptionTask'
        db.delete_table(u'transcripts_transcriptiontask')

        # Deleting model 'Transcript'
        db.delete_table(u'transcripts_transcript')

        # Deleting model 'TranscriptFragment'
        db.delete_table(u'transcripts_transcriptfragment')

        # Deleting model 'TranscriptFragmentRevision'
        db.delete_table(u'transcripts_transcriptfragmentrevision')

        # Deleting model 'TranscriptMedia'
        db.delete_table(u'transcripts_transcriptmedia')


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
        u'media.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'data_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'transcripts.sentencefragment': {
            'Meta': {'unique_together': "[('revision', 'sequence')]", 'object_name': 'SentenceFragment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentence_fragments'", 'to': u"orm['transcripts.TranscriptFragmentRevision']"}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'transcripts.transcript': {
            'Meta': {'object_name': 'Transcript'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'length_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unset'", 'max_length': '50'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'transcripts.transcriptfragment': {
            'Meta': {'unique_together': "[('transcript', 'start', 'end')]", 'object_name': 'TranscriptFragment'},
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unlocked'", 'max_length': '50'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'not_transcribed'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fragments'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.transcriptfragmentrevision': {
            'Meta': {'unique_together': "[('fragment', 'sequence')]", 'object_name': 'TranscriptFragmentRevision'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'fragment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': u"orm['transcripts.TranscriptFragment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'editing'", 'max_length': '50'})
        },
        u'transcripts.transcriptiontask': {
            'Meta': {'object_name': 'TranscriptionTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transcription_tasks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptFragmentRevision']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unassigned'", 'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.transcriptmedia': {
            'Meta': {'unique_together': "(('transcript', 'is_processed', 'is_full_length', 'start', 'end'),)", 'object_name': 'TranscriptMedia'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'end': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_full_length': ('django.db.models.fields.BooleanField', [], {}),
            'is_processed': ('django.db.models.fields.BooleanField', [], {}),
            'media_file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['media.MediaFile']"}),
            'start': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        }
    }

    complete_apps = ['transcripts']