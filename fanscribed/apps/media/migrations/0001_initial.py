# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaFile'
        db.create_table(u'media_mediafile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=1024)),
        ))
        db.send_create_signal(u'media', ['MediaFile'])


    def backwards(self, orm):
        # Deleting model 'MediaFile'
        db.delete_table(u'media_mediafile')


    models = {
        u'media.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'data_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['media']