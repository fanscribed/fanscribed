from uuid import uuid4

from django.conf import settings

from unipath import Path


STORAGE_PATH = Path(settings.MEDIAFILE_STORAGE_PATH).absolute()


def new_local_mediafile_path():
    return STORAGE_PATH.child(uuid4().hex)
