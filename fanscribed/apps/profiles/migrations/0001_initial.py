# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_fsm.db.fields.fsmfield


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nickname', models.CharField(max_length=100, null=True, blank=True)),
                ('nickname_slug', models.CharField(db_index=True, max_length=100, null=True, blank=True)),
                ('nickname_state', django_fsm.db.fields.fsmfield.FSMField(default=b'unset', max_length=50)),
                ('wants_reviews', models.BooleanField(default=False, help_text=b"Reviewing other's tasks helps finish transcripts faster.", verbose_name=b"Help review other's tasks.")),
                ('task_order', models.CharField(default=b'eager', max_length=10, verbose_name=b'Which order would you like to receive tasks?', choices=[(b'eager', b'Give me different kinds of tasks when they are available.'), (b'sequential', b'Give me the same kinds of tasks in sequence.')])),
            ],
        ),
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('description', models.CharField(max_length=200)),
                ('order', models.PositiveIntegerField(default=0, unique=True)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='task_types',
            field=models.ManyToManyField(to='profiles.TaskType', verbose_name=b'Which tasks would you like to help with?'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
