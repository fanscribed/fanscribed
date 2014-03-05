"""Functions for controlling and inspecting avconv."""

from decimal import Decimal
from subprocess import call, check_output

from unipath import Path


AVPROBE_PATH = '/usr/bin/avprobe'
_avprobe_alternatives = [
    '/usr/local/bin/avprobe',
    '/usr/bin/ffprobe',
    '/usr/local/bin/ffprobe',
]
for _candidate in _avprobe_alternatives:
    _candidate = Path(_candidate)
    # noinspection PyArgumentList
    if _candidate.exists():
        AVPROBE_PATH = _candidate


AVCONV_PATH = '/usr/bin/avconv'
_avconv_alternatives = [
    '/usr/local/bin/avconv',
    '/usr/bin/ffmpeg',
    '/usr/local/bin/ffmpeg',
]
for _candidate in _avconv_alternatives:
    _candidate = Path(_candidate)
    # noinspection PyArgumentList
    if _candidate.exists():
        AVCONV_PATH = _candidate


QUANTIZE_EXPONENT = Decimal('0.01')


def media_length(filename):
    """
    Use avconv to determine the length of the media.

    :param filename: Filename of media to inspect.
    :return: Length, in seconds of the media.
    """
    output = check_output([
        AVPROBE_PATH,
        '-loglevel', 'error',
        '-show_format',
        filename,
    ])
    for line in output.splitlines():
        if line.startswith('duration'):
            duration = line.strip().split('=')[1]
            duration = Decimal(duration).quantize(QUANTIZE_EXPONENT)
            return duration
    raise ValueError('Could not find duration for {filename}'.format(**locals()))


def convert(raw_file, processed_file, avconv_settings):
    """
    Convert a raw file to a processed file using the given list of settings.
    :param raw_file: Full path of raw file to read.
    :param processed_file: Full path of processed file to write.
    :param avconv_settings: List of strings of command-line options.
    :return: Exit code of avconv.
    """
    return call([
        AVCONV_PATH,
        '-i', raw_file
    ] + list(avconv_settings) + [
        processed_file,
    ])
