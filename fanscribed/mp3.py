"""Wrapper functions for controlling the 'mp3splt' tool."""

from hashlib import sha1
import os
import re
import subprocess


TOTAL_TIME_RE = re.compile(r'.*Total time: (\d+)m.(\d+)s')


def duration(filename):
    """Return the approximate duration, in milliseconds, of the given MP3 file."""
    mp3splt_output = subprocess.check_output(['mp3splt', '-qPft', '0.30.00', filename])
    duration = None
    for line in mp3splt_output.splitlines():
        match = TOTAL_TIME_RE.match(line)
        if match is not None:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            duration = (minutes * 60 + seconds) * 1000
            break
    if duration is None:
        raise IOError('Could not determine duration of MP3 file')
    else:
        return duration


def snippet_path(full_mp3, duration, output_path, starting_point, length, padding):
    """Extract a snippet of audio from a full MP3, and return its full path.

    All times are given in milliseconds.
    """
    ending_ms = starting_point + length + padding
    starting_point -= padding
    if starting_point < 0:
        starting_point = 0
    if ending_ms > duration:
        ending_ms = 0
    split_start = '{0:d}.{1:02d}.{2:02d}'.format(
        starting_point / 60000,
        starting_point % 60000 / 1000,
        starting_point % 1000 / 10,
    )
    split_end = '{0:d}.{1:02d}.{2:02d}'.format(
        ending_ms / 60000,
        ending_ms % 60000 / 1000,
        ending_ms % 1000 / 10,
    )
    # Generate a hashed filename based on source file, starting, and ending.
    hash = sha1('{0} {1} {2}'.format(full_mp3, split_start, split_end)).hexdigest()
    output_filename = os.path.join(output_path, '{0}.mp3'.format(hash))
    if os.path.isfile(output_filename):
        # File already exists; don't recreate it.
        # Instead, touch it so it doesn't get removed.
        with open(output_filename, 'a'):
            os.utime(output_filename, None)
        return output_filename
    else:
        subprocess.call([
            'mp3splt',
            '-Qf',
            '-d', output_path,
            '-o', hash,
            full_mp3,
            split_start,
            split_end,
        ])
        if not os.path.isfile(output_filename):
            raise IOError('Output file {0:r} was not generated'.format(output_filename))
        else:
            return output_filename
