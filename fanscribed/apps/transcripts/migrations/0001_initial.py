# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Transcript'
        db.create_table(u'transcripts_transcript', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('length', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'transcripts', ['Transcript'])

        # Adding model 'TranscriptMedia'
        db.create_table(u'transcripts_transcriptmedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.Transcript'])),
            ('media_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['media.MediaFile'])),
            ('is_processed', self.gf('django.db.models.fields.BooleanField')()),
            ('is_full_length', self.gf('django.db.models.fields.BooleanField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('start', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
            ('end', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'transcripts', ['TranscriptMedia'])

        # Adding unique constraint on 'TranscriptMedia', fields ['transcript', 'is_processed', 'is_full_length', 'start', 'end']
        db.create_unique(u'transcripts_transcriptmedia', ['transcript_id', 'is_processed', 'is_full_length', 'start', 'end'])


    def backwards(self, orm):
        # Removing unique constraint on 'TranscriptMedia', fields ['transcript', 'is_processed', 'is_full_length', 'start', 'end']
        db.delete_unique(u'transcripts_transcriptmedia', ['transcript_id', 'is_processed', 'is_full_length', 'start', 'end'])

        # Deleting model 'Transcript'
        db.delete_table(u'transcripts_transcript')

        # Deleting model 'TranscriptMedia'
        db.delete_table(u'transcripts_transcriptmedia')


    models = {
        u'media.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'data_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'transcripts.transcript': {
            'Meta': {'object_name': 'Transcript'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'transcripts.transcriptmedia': {
            'Meta': {'unique_together': "(('transcript', 'is_processed', 'is_full_length', 'start', 'end'),)", 'object_name': 'TranscriptMedia'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
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