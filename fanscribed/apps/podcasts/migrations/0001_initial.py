# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Podcast'
        db.create_table(u'podcasts_podcast', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('rss_url', self.gf('django.db.models.fields.URLField')(max_length=512)),
        ))
        db.send_create_signal(u'podcasts', ['Podcast'])

        # Adding model 'Episode'
        db.create_table(u'podcasts_episode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('podcast', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['podcasts.Podcast'])),
            ('title', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'podcasts', ['Episode'])

        # Adding model 'RssFetch'
        db.create_table(u'podcasts_rssfetch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')()),
            ('podcast', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['podcasts.Podcast'])),
            ('fetched', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.BinaryField')(null=True, blank=True)),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='not-fetched', max_length=50)),
        ))
        db.send_create_signal(u'podcasts', ['RssFetch'])


    def backwards(self, orm):
        # Deleting model 'Podcast'
        db.delete_table(u'podcasts_podcast')

        # Deleting model 'Episode'
        db.delete_table(u'podcasts_episode')

        # Deleting model 'RssFetch'
        db.delete_table(u'podcasts_rssfetch')


    models = {
        u'podcasts.episode': {
            'Meta': {'object_name': 'Episode'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['podcasts.Podcast']"}),
            'title': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'podcasts.podcast': {
            'Meta': {'object_name': 'Podcast'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rss_url': ('django.db.models.fields.URLField', [], {'max_length': '512'})
        },
        u'podcasts.rssfetch': {
            'Meta': {'object_name': 'RssFetch'},
            'body': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {}),
            'fetched': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['podcasts.Podcast']"}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'not-fetched'", 'max_length': '50'})
        }
    }

    complete_apps = ['podcasts']