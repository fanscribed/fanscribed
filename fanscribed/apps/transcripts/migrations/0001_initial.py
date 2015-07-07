# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm.db.fields.fsmfield
import model_utils.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BoundaryTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_review', models.BooleanField()),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'preparing', max_length=50)),
                ('presented_at', models.DateTimeField(null=True, blank=True)),
                ('validated_at', models.DateTimeField(null=True, blank=True)),
                ('start', models.DecimalField(max_digits=8, decimal_places=2)),
                ('end', models.DecimalField(max_digits=8, decimal_places=2)),
                ('assignee', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
                'permissions': (('add_boundarytask_review', 'Can add review boundary task'),),
            },
        ),
        migrations.CreateModel(
            name='CleanTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_review', models.BooleanField()),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'preparing', max_length=50)),
                ('presented_at', models.DateTimeField(null=True, blank=True)),
                ('validated_at', models.DateTimeField(null=True, blank=True)),
                ('text', models.TextField()),
                ('assignee', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
                'permissions': (('add_cleantask_review', 'Can add review clean task'),),
            },
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'empty', max_length=50)),
                ('clean_state', django_fsm.db.fields.fsmfield.FSMField(default=b'untouched', max_length=50)),
                ('clean_lock_id', models.CharField(max_length=32, null=True, blank=True)),
                ('boundary_state', django_fsm.db.fields.fsmfield.FSMField(default=b'untouched', max_length=50)),
                ('boundary_lock_id', models.CharField(max_length=32, null=True, blank=True)),
                ('speaker_state', django_fsm.db.fields.fsmfield.FSMField(default=b'untouched', max_length=50)),
                ('speaker_lock_id', models.CharField(max_length=32, null=True, blank=True)),
                ('tf_sequence', models.PositiveIntegerField()),
                ('latest_text', models.TextField(null=True, blank=True)),
                ('latest_start', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('latest_end', models.DecimalField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('boundary_last_editor', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('clean_last_editor', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('tf_start__start', 'tf_sequence'),
            },
        ),
        migrations.CreateModel(
            name='SentenceBoundary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.PositiveIntegerField()),
                ('start', models.DecimalField(max_digits=8, decimal_places=2)),
                ('end', models.DecimalField(max_digits=8, decimal_places=2)),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('sentence', models.ForeignKey(related_name='boundaries', to='transcripts.Sentence')),
            ],
            options={
                'ordering': ('sequence',),
                'get_latest_by': 'sequence',
            },
        ),
        migrations.CreateModel(
            name='SentenceFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.PositiveIntegerField()),
                ('text', models.TextField()),
            ],
            options={
                'ordering': ('revision__fragment__start', 'sequence'),
            },
        ),
        migrations.CreateModel(
            name='SentenceRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence', models.PositiveIntegerField()),
                ('text', models.TextField()),
                ('editor', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('sentence', models.ForeignKey(related_name='revisions', to='transcripts.Sentence')),
            ],
            options={
                'ordering': ('sequence',),
                'get_latest_by': 'sequence',
            },
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SpeakerTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_review', models.BooleanField()),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'preparing', max_length=50)),
                ('presented_at', models.DateTimeField(null=True, blank=True)),
                ('validated_at', models.DateTimeField(null=True, blank=True)),
                ('new_name', models.CharField(max_length=100, null=True, blank=True)),
                ('assignee', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
                'permissions': (('add_speakertask_review', 'Can add review speaker task'),),
            },
        ),
        migrations.CreateModel(
            name='StitchTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_review', models.BooleanField()),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'preparing', max_length=50)),
                ('presented_at', models.DateTimeField(null=True, blank=True)),
                ('validated_at', models.DateTimeField(null=True, blank=True)),
                ('assignee', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
                'get_latest_by': 'created',
                'permissions': (('add_stitchtask_review', 'Can add review stitch task'),),
            },
        ),
        migrations.CreateModel(
            name='StitchTaskPairing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('left', models.ForeignKey(related_name='+', to='transcripts.SentenceFragment')),
                ('right', models.ForeignKey(related_name='+', to='transcripts.SentenceFragment')),
                ('task', models.ForeignKey(related_name='pairings', to='transcripts.StitchTask')),
            ],
            options={
                'ordering': ('left__revision__fragment__start', 'left__sequence'),
            },
        ),
        migrations.CreateModel(
            name='TranscribeTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('is_review', models.BooleanField()),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'preparing', max_length=50)),
                ('presented_at', models.DateTimeField(null=True, blank=True)),
                ('validated_at', models.DateTimeField(null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('start', models.DecimalField(max_digits=8, decimal_places=2)),
                ('end', models.DecimalField(max_digits=8, decimal_places=2)),
                ('assignee', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created',),
                'permissions': (('add_transcribetask_review', 'Can add review transcribe task'),),
            },
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('title', models.CharField(max_length=512)),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'unfinished', max_length=50)),
                ('length', models.DecimalField(null=True, max_digits=8, decimal_places=2)),
                ('length_state', django_fsm.db.fields.fsmfield.FSMField(default=b'unset', max_length=50)),
                ('contributors', models.ManyToManyField(related_name='contributed_to_transcripts', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='TranscriptFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DecimalField(max_digits=8, decimal_places=2)),
                ('end', models.DecimalField(max_digits=8, decimal_places=2)),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'empty', max_length=50)),
                ('lock_state', django_fsm.db.fields.fsmfield.FSMField(default=b'unlocked', max_length=50)),
                ('lock_id', models.CharField(max_length=32, null=True, blank=True)),
                ('last_editor', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('transcript', models.ForeignKey(related_name='fragments', to='transcripts.Transcript')),
            ],
            options={
                'ordering': ('start',),
            },
        ),
        migrations.CreateModel(
            name='TranscriptFragmentRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('sequence', models.PositiveIntegerField()),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('fragment', models.ForeignKey(related_name='revisions', to='transcripts.TranscriptFragment')),
            ],
            options={
                'ordering': ('sequence',),
                'get_latest_by': 'sequence',
            },
        ),
        migrations.CreateModel(
            name='TranscriptMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('file', models.FileField(max_length=1024, upload_to=b'transcripts')),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'empty', max_length=50)),
                ('is_processed', models.BooleanField(help_text=b'Is it processed media?')),
                ('is_full_length', models.BooleanField(help_text=b'Is it the full length of media to be transcribed?')),
                ('start', models.DecimalField(null=True, max_digits=8, decimal_places=2)),
                ('end', models.DecimalField(null=True, max_digits=8, decimal_places=2)),
                ('download_count', models.PositiveIntegerField(default=0)),
                ('transcript', models.ForeignKey(related_name='media', to='transcripts.Transcript')),
            ],
        ),
        migrations.CreateModel(
            name='TranscriptStitch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'notready', max_length=50)),
                ('lock_state', django_fsm.db.fields.fsmfield.FSMField(default=b'unlocked', max_length=50)),
                ('lock_id', models.CharField(max_length=32, null=True, blank=True)),
                ('last_editor', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('left', models.OneToOneField(related_name='stitch_at_right', to='transcripts.TranscriptFragment')),
                ('right', models.OneToOneField(related_name='stitch_at_left', to='transcripts.TranscriptFragment')),
                ('transcript', models.ForeignKey(related_name='stitches', to='transcripts.Transcript')),
            ],
            options={
                'ordering': ('left__start',),
            },
        ),
        migrations.AddField(
            model_name='transcribetask',
            name='fragment',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptFragment', null=True),
        ),
        migrations.AddField(
            model_name='transcribetask',
            name='media',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptMedia', null=True),
        ),
        migrations.AddField(
            model_name='transcribetask',
            name='revision',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptFragmentRevision', null=True),
        ),
        migrations.AddField(
            model_name='transcribetask',
            name='transcript',
            field=models.ForeignKey(to='transcripts.Transcript'),
        ),
        migrations.AddField(
            model_name='stitchtask',
            name='media',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptMedia', null=True),
        ),
        migrations.AddField(
            model_name='stitchtask',
            name='stitch',
            field=models.ForeignKey(related_name='+', to='transcripts.TranscriptStitch'),
        ),
        migrations.AddField(
            model_name='stitchtask',
            name='transcript',
            field=models.ForeignKey(to='transcripts.Transcript'),
        ),
        migrations.AddField(
            model_name='speakertask',
            name='media',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptMedia', null=True),
        ),
        migrations.AddField(
            model_name='speakertask',
            name='sentence',
            field=models.ForeignKey(to='transcripts.Sentence'),
        ),
        migrations.AddField(
            model_name='speakertask',
            name='speaker',
            field=models.ForeignKey(blank=True, to='transcripts.Speaker', null=True),
        ),
        migrations.AddField(
            model_name='speakertask',
            name='transcript',
            field=models.ForeignKey(to='transcripts.Transcript'),
        ),
        migrations.AddField(
            model_name='speaker',
            name='transcript',
            field=models.ForeignKey(related_name='speakers', to='transcripts.Transcript'),
        ),
        migrations.AddField(
            model_name='sentencefragment',
            name='revision',
            field=models.ForeignKey(related_name='sentence_fragments', to='transcripts.TranscriptFragmentRevision'),
        ),
        migrations.AddField(
            model_name='sentence',
            name='fragment_candidates',
            field=models.ManyToManyField(related_name='candidate_sentences', to='transcripts.SentenceFragment'),
        ),
        migrations.AddField(
            model_name='sentence',
            name='fragments',
            field=models.ManyToManyField(related_name='sentences', to='transcripts.SentenceFragment'),
        ),
        migrations.AddField(
            model_name='sentence',
            name='latest_speaker',
            field=models.ForeignKey(blank=True, to='transcripts.Speaker', null=True),
        ),
        migrations.AddField(
            model_name='sentence',
            name='speaker_last_editor',
            field=models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='sentence',
            name='tf_start',
            field=models.ForeignKey(to='transcripts.TranscriptFragment'),
        ),
        migrations.AddField(
            model_name='sentence',
            name='transcript',
            field=models.ForeignKey(related_name='sentences', to='transcripts.Transcript'),
        ),
        migrations.AddField(
            model_name='cleantask',
            name='media',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptMedia', null=True),
        ),
        migrations.AddField(
            model_name='cleantask',
            name='sentence',
            field=models.ForeignKey(to='transcripts.Sentence'),
        ),
        migrations.AddField(
            model_name='cleantask',
            name='transcript',
            field=models.ForeignKey(to='transcripts.Transcript'),
        ),
        migrations.AddField(
            model_name='boundarytask',
            name='media',
            field=models.ForeignKey(blank=True, to='transcripts.TranscriptMedia', null=True),
        ),
        migrations.AddField(
            model_name='boundarytask',
            name='sentence',
            field=models.ForeignKey(to='transcripts.Sentence'),
        ),
        migrations.AddField(
            model_name='boundarytask',
            name='transcript',
            field=models.ForeignKey(to='transcripts.Transcript'),
        ),
        migrations.AlterUniqueTogether(
            name='transcriptstitch',
            unique_together=set([('transcript', 'left')]),
        ),
        migrations.AlterUniqueTogether(
            name='transcriptmedia',
            unique_together=set([('transcript', 'is_processed', 'is_full_length', 'start', 'end')]),
        ),
        migrations.AlterUniqueTogether(
            name='transcriptfragmentrevision',
            unique_together=set([('fragment', 'sequence')]),
        ),
        migrations.AlterUniqueTogether(
            name='transcriptfragment',
            unique_together=set([('transcript', 'start', 'end')]),
        ),
        migrations.AlterUniqueTogether(
            name='stitchtaskpairing',
            unique_together=set([('task', 'left')]),
        ),
        migrations.AlterUniqueTogether(
            name='speaker',
            unique_together=set([('transcript', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='sentencerevision',
            unique_together=set([('sentence', 'sequence')]),
        ),
        migrations.AlterUniqueTogether(
            name='sentencefragment',
            unique_together=set([('revision', 'sequence')]),
        ),
        migrations.AlterUniqueTogether(
            name='sentenceboundary',
            unique_together=set([('sentence', 'sequence')]),
        ),
    ]
