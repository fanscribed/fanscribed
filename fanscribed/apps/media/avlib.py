"""Functions for controlling and inspecting avconv."""

from decimal import Decimal
from subprocess import call, check_output
import sys

from django.conf import settings


if sys.platform == 'linux2':

    AVPROBE_PATH = getattr(settings, 'AVPROBE_PATH', '/usr/bin/avprobe')
    AVPROBE_ARGS = [
        '-loglevel', 'error',
        '-f', 'mp3',
        '-show_format',
    ]
    AVCONV_PATH = getattr(settings, 'AVCONV_PATH', '/usr/bin/avconv')
    AVCONV_ARGS = [
        '-f', 'mp3',
        '-i',
    ]

elif sys.platform == 'darwin':

    AVPROBE_PATH = getattr(settings, 'AVPROBE_PATH', '/usr/local/bin/ffprobe')
    AVPROBE_ARGS = [
        '-loglevel', 'error',
        '-f', 'mp3',
        '-show_format',
    ]
    AVCONV_PATH = getattr(settings, 'AVCONV_PATH', '/usr/local/bin/ffmpeg')
    AVCONV_ARGS = [
        '-f', 'mp3',
        '-i',
    ]


QUANTIZE_EXPONENT = Decimal('0.01')


def media_length(filename):
    """
    Use avconv to determine the length of the media.

    :param filename: Filename of media to inspect.
    :return: Length, in seconds of the media.
    """
    args = (
        [AVPROBE_PATH]
        + AVPROBE_ARGS
        + [filename]
    )
    output = check_output(args)
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
    args = (
        [AVCONV_PATH]
        + AVCONV_ARGS
        + [raw_file]
        + list(avconv_settings)
        + [processed_file]
    )
    return call(args)
