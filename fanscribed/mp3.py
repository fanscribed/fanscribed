"""Wrapper functions for controlling the 'mp3splt' tool."""

import re
import subprocess


TOTAL_TIME_RE = re.compile(r'.*Total time: (\d+)m.(\d+)s')


def duration_ms(filename):
    """Return the approximate duration, in ms, of the given MP3 file."""
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
