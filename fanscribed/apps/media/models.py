from hashlib import sha1
import random
from shutil import copyfile, move
from urlparse import urlsplit

from django.conf import settings
from django.db import models

import requests

from unipath import Path


CACHE_PATH = Path(settings.MEDIAFILE_CACHE_PATH).absolute()


class MediaFile(models.Model):

    data_url = models.URLField(max_length=1024, unique=True)

    def __unicode__(self):
        return '{} ({})'.format(self.id, self.data_url)

    def local_cache_path(self):
        """Return local cache path for this media file, fetching as needed."""

        url_hash = sha1(self.data_url).hexdigest()
        cache_file = CACHE_PATH.child(url_hash)

        # If it's already cached, use it.
        if cache_file.exists():
            return cache_file

        # Not cached; retrieve and store it.
        url = urlsplit(self.data_url)

        # Start out with a temp file, to avoid one process clobbering another.
        temp_file = '{}_{}'.format(cache_file, random.randint(10000, 99999))

        if url.scheme == 'file':
            source = url.path
            copyfile(source, temp_file)

        elif url.scheme.startswith('http'):
            response = requests.get(self.data_url, stream=True)
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=16384):
                    f.write(chunk)

        else:
            raise ValueError(
                'Unrecognized URL scheme {url.scheme!r}'.format(**locals()))

        # Success with either file, http, or https.
        move(temp_file, cache_file)
        return cache_file
