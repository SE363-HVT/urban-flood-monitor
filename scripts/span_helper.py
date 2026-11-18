"""Build spans from reviewed phrases with explicit occurrence selection.

Never edits text/files. Invalid boundaries are rejected, not silently changed.
"""
if __package__:
    from .aste_audit_core import LOCATIVE_PREPS, POLARITIES, is_edge_punctuation, span_problem
else:
    from aste_audit_core import LOCATIVE_PREPS, POLARITIES, is_edge_punctuation, span_problem

bad_preps = sorted(LOCATIVE_PREPS)
bad_puncts = [',', '.', '!', '?', ';', ':', '(', ')', '"', '“', '”', '…', '#']


def find_subsequence(tokens, phrase_words, *, occurrence=None, start=None):
    """Exact, case-sensitive tokens; occurrence is zero based, start absolute.

    Repeated phrases require explicit selection. None means phrase absent.
    """
    if not phrase_words:
        raise ValueError('Phrase cannot be empty.')
    if occurrence is not None and start is not None:
        raise ValueError('Choose occurrence OR start, not both.')
    matches = [i for i in range(len(tokens) - len(phrase_words) + 1)
               if tokens[i:i + len(phrase_words)] == phrase_words]
    if start is not None:
        if type(start) is not int or start not in matches:
            raise ValueError(f'Phrase does not match at start={start!r}; candidates={matches}.')
        chosen = start
    elif occurrence is not None:
        if type(occurrence) is not int or not 0 <= occurrence < len(matches):
            raise ValueError(f'Invalid occurrence={occurrence!r}; candidates={matches}.')
        chosen = matches[occurrence]
    elif not matches:
        return None
    elif len(matches) != 1:
        raise ValueError(f'Ambiguous phrase; select occurrence or start. Candidate starts={matches}.')
    else:
        chosen = matches[0]
    return list(range(chosen, chosen + len(phrase_words)))


def sanitize_span(tokens, idx_list, is_aspect=True):
    """Explicit opt-in trimming; make_triplet never silently calls this.

    Review returned words before using them. 'khu' is not a banned locative.
    """
    problem = span_problem(tokens, idx_list)
    if problem:
        raise ValueError(problem[1])
    result = list(idx_list)
    while result and (is_edge_punctuation(tokens[result[0]]) or
                      (is_aspect and tokens[result[0]].casefold() in LOCATIVE_PREPS)):
        result.pop(0)
    while result and is_edge_punctuation(tokens[result[-1]]):
        result.pop()
    return result


def make_triplet(text, asp_phrase, opi_phrase, polarity, *, asp_occurrence=None,
                 opi_occurrence=None, asp_start=None, opi_start=None):
    if not all(isinstance(value, str) for value in (text, asp_phrase, opi_phrase)):
        raise ValueError('Text, aspect phrase and opinion phrase must be strings.')
    tokens = text.split()
    if not isinstance(polarity, str) or polarity not in POLARITIES:
        raise ValueError('Polarity must be POS, NEG or NEU.')
    aspect = find_subsequence(tokens, asp_phrase.split(), occurrence=asp_occurrence, start=asp_start)
    opinion = find_subsequence(tokens, opi_phrase.split(), occurrence=opi_occurrence, start=opi_start)
    if aspect is None or opinion is None:
        raise ValueError('Reviewed phrase not found verbatim in final text.')
    for name, span in [('Aspect', aspect), ('Opinion', opinion)]:
        if is_edge_punctuation(tokens[span[0]]) or is_edge_punctuation(tokens[span[-1]]):
            raise ValueError(f'{name} has edge punctuation/emoji; select corrected phrase explicitly.')
    if tokens[aspect[0]].casefold() in LOCATIVE_PREPS:
        raise ValueError('Aspect starts with a locative; select corrected phrase explicitly.')
    if set(aspect) & set(opinion):
        raise ValueError(f'Aspect/opinion overlap: {aspect}, {opinion}.')
    return (aspect, opinion, polarity)
