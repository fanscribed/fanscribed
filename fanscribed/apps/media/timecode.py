"""Functions related to timecodes."""


def decimal_to_timecode(decimal):
    min = int(decimal / 60)
    sec = int(decimal - (min * 60))
    frac = int((decimal - (min * 60)) * 100) % 100
    timecode = '{min:02d}.{sec:02d}.{frac:02d}'.format(**locals())
    return timecode
