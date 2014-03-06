"""Functions for controlling and inspecting avconv."""

from decimal import Decimal
from subprocess import call, check_output

from django.conf import settings


AVPROBE_PATH = getattr(settings, 'AVPROBE_PATH', '/usr/bin/avprobe')
AVCONV_PATH = getattr(settings, 'AVCONV_PATH', '/usr/bin/avconv')

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
