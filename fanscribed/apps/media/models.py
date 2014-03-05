from django.db import models


class MediaFile(models.Model):

    data_url = models.URLField(max_length=1024, unique=True)

    def __unicode__(self):
        return '{} ({})'.format(self.id, self.data_url)
