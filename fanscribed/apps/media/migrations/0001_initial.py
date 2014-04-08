# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('transcripts', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'TranscriptMedia'
        db.create_table(u'media_transcriptmedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(related_name='media', to=orm['transcripts.Transcript'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=1024)),
            ('is_processed', self.gf('django.db.models.fields.BooleanField')()),
            ('is_full_length', self.gf('django.db.models.fields.BooleanField')()),
            ('start', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
            ('end', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'media', ['TranscriptMedia'])

        # Adding unique constraint on 'TranscriptMedia', fields ['transcript', 'is_processed', 'is_full_length', 'start', 'end']
        db.create_unique(u'media_transcriptmedia', ['transcript_id', 'is_processed', 'is_full_length', 'start', 'end'])


    def backwards(self, orm):
        # Removing unique constraint on 'TranscriptMedia', fields ['transcript', 'is_processed', 'is_full_length', 'start', 'end']
        db.delete_unique(u'media_transcriptmedia', ['transcript_id', 'is_processed', 'is_full_length', 'start', 'end'])

        # Deleting model 'TranscriptMedia'
        db.delete_table(u'media_transcriptmedia')


    models = {
        u'media.transcriptmedia': {
            'Meta': {'unique_together': "(('transcript', 'is_processed', 'is_full_length', 'start', 'end'),)", 'object_name': 'TranscriptMedia'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'end': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_full_length': ('django.db.models.fields.BooleanField', [], {}),
            'is_processed': ('django.db.models.fields.BooleanField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'start': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'media'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.transcript': {
            'Meta': {'object_name': 'Transcript'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'length_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unset'", 'max_length': '50'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['media']