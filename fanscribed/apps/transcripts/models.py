from django.db import models

from django_extensions.db.models import CreationDateTimeField

from django_fsm.db.fields import FSMField


class Transcript(models.Model):

    created = CreationDateTimeField()
    name = models.CharField(max_length=512)
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    length_state = FSMField(default='not-determined', protected=True)

    def __unicode__(self):
        return self.name
