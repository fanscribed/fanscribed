def dialogue_list(original_text):
    """Return a list of dialogue parts for the given original text.

    Each dialogue part is a dictionary::

        dict(
            abbreviation=ABBREVIATION,
            lines=[
                SPOKEN_TEXT_LINE,
                ...
            ],
        )
    """
    def append_line(text):
        current_part['lines'].append(text)
    def append_part_if_not_empty():
        if current_part['lines']:
            parts.append(current_part)
    def new_part(abbreviation=None):
        return dict(
            abbreviation=abbreviation,
            lines=[],
        )
    parts = []
    current_part = new_part()
    for line in original_text.splitlines():
        line = line.strip()
        if u';' not in line:
            # Only text was given.
            abbreviation = current_part['abbreviation'] or None
            text = line.strip()
        else:
            # Speaker abbreviation and text were given.
            abbreviation, text = line.split(u';', 1)
            abbreviation = abbreviation.strip() or None
            text = text.strip()
        #
        if not text:
            # Skip blank line.
            continue
        else:
            # Process non-blank line.
            pass
        #
        if abbreviation is None:
            # Use current abbreviation if none given in text.
            abbreviation = current_part['abbreviation']
        else:
            # Use given abbreviation.
            pass
        #
        if current_part['abbreviation'] is None and not current_part['lines']:
            # First part, so initialize its abbreviation.
            current_part['abbreviation'] = abbreviation
        elif abbreviation != current_part['abbreviation']:
            # New speaker found; add to a new part.
            append_part_if_not_empty()
            current_part = new_part(abbreviation)
        else:
            # Existing speaker; add to existing part.
            pass
        #
        append_line(text)
    # All done, append the final part.
    append_part_if_not_empty()
    return parts


def normalized_text(original_text):
    """Return a normalized rendition of the given original text."""
    return u'\n\n'.join(
        '\n'.join(
            u'{abbreviation};{line}'.format(
                abbreviation=(part['abbreviation'] or '') if index == 0 else '',
                line=line,
            )
            for index, line
            in enumerate(part['lines'])
        )
        for part
        in dialogue_list(original_text)
    )
