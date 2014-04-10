"""Functions for controlling the mp3splt utility."""

import os
from subprocess import check_output, STDOUT

from django.conf import settings
from unipath import Path

from .timecode import decimal_to_timecode


MP3SPLT_PATH = getattr(settings, 'MP3SPLT_PATH', '/usr/bin/mp3splt')
_mp3splt_alternatives = [
    '/usr/local/bin/mp3splt',
]
for _candidate in _mp3splt_alternatives:
    _candidate = Path(_candidate)
    # noinspection PyArgumentList
    if _candidate.exists():
        MP3SPLT_PATH = _candidate


def extract_segment(full_length_file, slice_file, start, end):
    """
    Extract a slice of a full-length file.

    :param full_length_file: Filename of full-length MP3 file.
    :param slice_file: Filename of slice MP3 file to create.
    :param start: Start time in seconds.  (.01 resolution)
    :param end: End time in seconds.  (.01 resolution)
    """

    if start < 0.00:
        raise ValueError('start must be positive')

    if end <= start:
        raise ValueError('end must be after start')

    start_timecode = decimal_to_timecode(start)
    end_timecode = decimal_to_timecode(end)

    slice_file_basename = os.path.basename(slice_file)
    slice_file_dirname = os.path.dirname(slice_file)

    check_output([
        MP3SPLT_PATH,
        '-o', slice_file_basename,
        '-d', slice_file_dirname,
        full_length_file,
        start_timecode,
        end_timecode,
    ], stderr=STDOUT)
    # (mp3splt adds an extra '.mp3' to the filename)
    os.rename(slice_file + '.mp3', slice_file)
