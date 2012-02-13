"""Simple filesystem-based cache."""

import hashlib
import os
import random
import time

from fanscribed.common import app_settings


def _cache_path():
    path = app_settings()['fanscribed.cache']
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_cached_content(key):
    """Return (content, mtime) associated with ``key``, or ``(None, None)`` if not found."""
    # Convert key to a hash.
    hashed_key = hashlib.sha1(str(key)).hexdigest()
    # Load it if it exists.
    content_path = os.path.join(_cache_path(), hashed_key)
    try:
        with open(content_path, 'rb') as f:
            return f.read(), os.fstat(f.fileno()).st_mtime
    except IOError:
        return None, None


def cache_content(key, content, mtime=None):
    """Cache the given content."""
    # Convert key to a hash.
    hashed_key = hashlib.sha1(str(key)).hexdigest()
    # Convert to bytes as needed. TODO: should we be doing this here?
    if isinstance(content, unicode):
        content = content.encode('utf8')
    # Write to a temporary file, then rename, to make cache writes atomic
    # in the event of race conditions.
    cache_path = _cache_path()
    initial_path = os.path.join(cache_path, '{0}-{1}'.format(hashed_key, random.random()))
    final_path = os.path.join(cache_path, hashed_key)
    with open(initial_path, 'wb') as f:
        f.write(content)
    if mtime is not None:
        os.utime(initial_path, (time.time(), mtime))
    os.rename(initial_path, final_path)
