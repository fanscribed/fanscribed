# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sentence'
        db.create_table(u'transcripts_sentence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sentences', to=orm['transcripts.Transcript'])),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='empty', max_length=50)),
            ('tf_start', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.TranscriptFragment'])),
            ('tf_sequence', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'transcripts', ['Sentence'])

        # Adding M2M table for field fragments on 'Sentence'
        m2m_table_name = db.shorten_name(u'transcripts_sentence_fragments')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sentence', models.ForeignKey(orm[u'transcripts.sentence'], null=False)),
            ('sentencefragment', models.ForeignKey(orm[u'transcripts.sentencefragment'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sentence_id', 'sentencefragment_id'])

        # Adding M2M table for field fragment_candidates on 'Sentence'
        m2m_table_name = db.shorten_name(u'transcripts_sentence_fragment_candidates')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sentence', models.ForeignKey(orm[u'transcripts.sentence'], null=False)),
            ('sentencefragment', models.ForeignKey(orm[u'transcripts.sentencefragment'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sentence_id', 'sentencefragment_id'])

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

        # Adding model 'TranscribeTask'
        db.create_table(u'transcripts_transcribetask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.Transcript'])),
            ('is_review', self.gf('django.db.models.fields.BooleanField')()),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unassigned', max_length=50)),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('revision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.TranscriptFragmentRevision'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('end', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'transcripts', ['TranscribeTask'])

        # Adding model 'StitchTask'
        db.create_table(u'transcripts_stitchtask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('transcript', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['transcripts.Transcript'])),
            ('is_review', self.gf('django.db.models.fields.BooleanField')()),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unassigned', max_length=50)),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('left', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['transcripts.TranscriptFragmentRevision'])),
            ('right', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['transcripts.TranscriptFragmentRevision'])),
        ))
        db.send_create_signal(u'transcripts', ['StitchTask'])

        # Adding model 'StitchTaskPairing'
        db.create_table(u'transcripts_stitchtaskpairing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='task_pairings', to=orm['transcripts.StitchTask'])),
            ('left', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['transcripts.SentenceFragment'])),
            ('right', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['transcripts.SentenceFragment'])),
        ))
        db.send_create_signal(u'transcripts', ['StitchTaskPairing'])

        # Adding unique constraint on 'StitchTaskPairing', fields ['task', 'left']
        db.create_unique(u'transcripts_stitchtaskpairing', ['task_id', 'left_id'])

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
            ('stitched_left', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('stitched_right', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='empty', max_length=50)),
            ('lock_state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='unlocked', max_length=50)),
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

        # Removing unique constraint on 'StitchTaskPairing', fields ['task', 'left']
        db.delete_unique(u'transcripts_stitchtaskpairing', ['task_id', 'left_id'])

        # Removing unique constraint on 'SentenceFragment', fields ['revision', 'sequence']
        db.delete_unique(u'transcripts_sentencefragment', ['revision_id', 'sequence'])

        # Deleting model 'Sentence'
        db.delete_table(u'transcripts_sentence')

        # Removing M2M table for field fragments on 'Sentence'
        db.delete_table(db.shorten_name(u'transcripts_sentence_fragments'))

        # Removing M2M table for field fragment_candidates on 'Sentence'
        db.delete_table(db.shorten_name(u'transcripts_sentence_fragment_candidates'))

        # Deleting model 'SentenceFragment'
        db.delete_table(u'transcripts_sentencefragment')

        # Deleting model 'TranscribeTask'
        db.delete_table(u'transcripts_transcribetask')

        # Deleting model 'StitchTask'
        db.delete_table(u'transcripts_stitchtask')

        # Deleting model 'StitchTaskPairing'
        db.delete_table(u'transcripts_stitchtaskpairing')

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
        u'transcripts.sentence': {
            'Meta': {'ordering': "('tf_start__start', 'tf_sequence')", 'object_name': 'Sentence'},
            'fragment_candidates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'candidate_sentences'", 'symmetrical': 'False', 'to': u"orm['transcripts.SentenceFragment']"}),
            'fragments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sentences'", 'symmetrical': 'False', 'to': u"orm['transcripts.SentenceFragment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'empty'", 'max_length': '50'}),
            'tf_sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tf_start': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptFragment']"}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentences'", 'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.sentencefragment': {
            'Meta': {'ordering': "('revision__fragment__start', 'sequence')", 'unique_together': "[('revision', 'sequence')]", 'object_name': 'SentenceFragment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentence_fragments'", 'to': u"orm['transcripts.TranscriptFragmentRevision']"}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'transcripts.stitchtask': {
            'Meta': {'object_name': 'StitchTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.TranscriptFragmentRevision']"}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.TranscriptFragmentRevision']"}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unassigned'", 'max_length': '50'}),
            'transcript': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.Transcript']"})
        },
        u'transcripts.stitchtaskpairing': {
            'Meta': {'unique_together': "[('task', 'left')]", 'object_name': 'StitchTaskPairing'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.SentenceFragment']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['transcripts.SentenceFragment']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'task_pairings'", 'to': u"orm['transcripts.StitchTask']"})
        },
        u'transcripts.transcribetask': {
            'Meta': {'object_name': 'TranscribeTask'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_review': ('django.db.models.fields.BooleanField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['transcripts.TranscriptFragmentRevision']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unassigned'", 'max_length': '50'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'transcripts.transcriptfragment': {
            'Meta': {'ordering': "('start',)", 'unique_together': "[('transcript', 'start', 'end')]", 'object_name': 'TranscriptFragment'},
            'end': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lock_state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'unlocked'", 'max_length': '50'}),
            'start': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'empty'", 'max_length': '50'}),
            'stitched_left': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stitched_right': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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