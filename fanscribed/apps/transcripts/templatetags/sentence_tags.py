from django import template


register = template.Library()


@register.filter()
def cleanupcandidates(sentence):
    """Find candidates for cleaned up sentence text using overlap detection."""
    already_yielded = set()
    sentence_text = sentence.text

    def combine(first, rest):
        if not rest:
            if first.text != sentence_text:
                yield first.text
        else:
            first_str = first.text
            rest_str = u' '.join(fragment.text for fragment in rest)
            candidate1 = overlapped_join(first_str, rest_str)
            candidate2 = simple_join(first_str, rest_str)
            for candidate in [candidate1, candidate2]:
                if candidate is not None and candidate not in already_yielded:
                    if candidate != sentence_text:
                        yield candidate
                    already_yielded.add(candidate)

    fragments = list(sentence.fragments.all())
    return list(combine(fragments[0], fragments[1:]))


def simple_join(first, second):
    return u' '.join([first, second])


def overlapped_join(first, second):
    # TODO: describe this algorithm
    # (This is some dark magic I originally conjured on April 8, 2013)
    first_lower = first.lower()
    second_lower = second.lower()
    is_duplicate = (first_lower == second_lower)
    if is_duplicate:
        return first
    i = 0
    while i != -1:
        first_part = first_lower[i:]
        prev_char = first_lower[i - 1]
        at_word_boundary = (i == 0) or (prev_char == u' ')
        does_overlap = second_lower.startswith(first_part)
        is_duplicate = (second_lower == first_part)
        if at_word_boundary and (does_overlap or is_duplicate):
            overlap_len = len(first) - i
            return u''.join([first, second[overlap_len:]])
        i = first_lower.find(u' ', i + 1) + 1
