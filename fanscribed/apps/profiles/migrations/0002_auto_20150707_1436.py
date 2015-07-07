# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_default_task_types(apps, schema_editor):
    TaskType = apps.get_model('profiles', 'TaskType')
    for order, (name, description) in enumerate([
        ('transcribe', 'Transcribe speech to text.'),
        ('stitch', 'Combine sentence fragments into complete sentences.'),
        ('boundary', 'Find start and end time codes for sentences.'),
        ('clean', 'Clean up text of sentences to remove repeated words, and correct capitalization and punctuation.'),
        ('speaker', 'Identify speakers of sentences.'),
    ], start=1):
        TaskType.objects.get_or_create(
            order=order,
            name=name,
            description=description,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_task_types)
    ]
