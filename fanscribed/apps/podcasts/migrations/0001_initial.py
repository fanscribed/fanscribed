# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django_fsm.db.fields.fsmfield
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transcripts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=512)),
                ('title', models.CharField(max_length=512)),
                ('published', models.DateTimeField()),
                ('media_url', models.URLField(max_length=512)),
                ('link_url', models.URLField(max_length=512, null=True, blank=True)),
                ('image_url', models.URLField(max_length=512, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('external_transcript', models.URLField(max_length=512, null=True, blank=True)),
            ],
            options={
                'ordering': ('-published',),
            },
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rss_url', models.URLField(unique=True, max_length=512)),
                ('approval_state', django_fsm.db.fields.fsmfield.FSMField(default=b'not_approved', max_length=50)),
                ('title', models.CharField(max_length=512, null=True, blank=True)),
                ('link_url', models.URLField(max_length=512, null=True, blank=True)),
                ('image_url', models.URLField(max_length=512, null=True, blank=True)),
                ('provides_own_transcripts', models.BooleanField(default=False, help_text=b"If True, episodes have external transcript set to the episode's link URL")),
            ],
            options={
                'ordering': ('title', 'rss_url'),
            },
        ),
        migrations.CreateModel(
            name='RssFetch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('fetched', models.DateTimeField(null=True, blank=True)),
                ('body', models.BinaryField(null=True, blank=True)),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'not_fetched', max_length=50)),
                ('podcast', models.ForeignKey(related_name='fetches', to='podcasts.Podcast')),
            ],
        ),
        migrations.CreateModel(
            name='TranscriptionApproval',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('approval_type', models.CharField(max_length=5, choices=[(b'user', b'User'), (b'staff', b'Staff'), (b'owner', b'Owner')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('podcast', models.ForeignKey(related_name='approvals', to='podcasts.Podcast')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='podcast',
            field=models.ForeignKey(related_name='episodes', to='podcasts.Podcast'),
        ),
        migrations.AddField(
            model_name='episode',
            name='transcript',
            field=models.OneToOneField(related_name='episode', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='transcripts.Transcript'),
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('podcast', 'guid')]),
        ),
    ]
