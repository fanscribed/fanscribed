# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Episode'
        db.create_table(u'podcasts_episode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('podcast', self.gf('django.db.models.fields.related.ForeignKey')(related_name='episodes', to=orm['podcasts.Podcast'])),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('published', self.gf('django.db.models.fields.DateTimeField')()),
            ('media_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'podcasts', ['Episode'])

        # Adding unique constraint on 'Episode', fields ['podcast', 'guid']
        db.create_unique(u'podcasts_episode', ['podcast_id', 'guid'])

        # Adding model 'Podcast'
        db.create_table(u'podcasts_podcast', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rss_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('approval_state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='not_approved', max_length=50)),
        ))
        db.send_create_signal(u'podcasts', ['Podcast'])

        # Adding model 'RssFetch'
        db.create_table(u'podcasts_rssfetch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('podcast', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fetches', to=orm['podcasts.Podcast'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('fetched', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.BinaryField')(null=True, blank=True)),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='not_fetched', max_length=50)),
        ))
        db.send_create_signal(u'podcasts', ['RssFetch'])

        # Adding model 'TranscriptionApproval'
        db.create_table(u'podcasts_transcriptionapproval', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('podcast', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['podcasts.Podcast'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('approval_type', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'podcasts', ['TranscriptionApproval'])


    def backwards(self, orm):
        # Removing unique constraint on 'Episode', fields ['podcast', 'guid']
        db.delete_unique(u'podcasts_episode', ['podcast_id', 'guid'])

        # Deleting model 'Episode'
        db.delete_table(u'podcasts_episode')

        # Deleting model 'Podcast'
        db.delete_table(u'podcasts_podcast')

        # Deleting model 'RssFetch'
        db.delete_table(u'podcasts_rssfetch')

        # Deleting model 'TranscriptionApproval'
        db.delete_table(u'podcasts_transcriptionapproval')


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
        u'podcasts.episode': {
            'Meta': {'unique_together': "[('podcast', 'guid')]", 'object_name': 'Episode'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'episodes'", 'to': u"orm['podcasts.Podcast']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'podcasts.podcast': {
            'Meta': {'object_name': 'Podcast'},
            'approval_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'not_approved'", 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rss_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'podcasts.rssfetch': {
            'Meta': {'object_name': 'RssFetch'},
            'body': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'fetched': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fetches'", 'to': u"orm['podcasts.Podcast']"}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'not_fetched'", 'max_length': '50'})
        },
        u'podcasts.transcriptionapproval': {
            'Meta': {'object_name': 'TranscriptionApproval'},
            'approval_type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['podcasts.Podcast']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['podcasts']