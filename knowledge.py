"""Knowledge in learning, Chapter 19"""

from random import shuffle
from utils import powerset


def current_best_learning(examples, h, examples_so_far=[]):
    """ [Figure 19.2]
    The hypothesis is a dictionary in the following form:
    * The keys are the attribute names.
    * The NOT operation is denoted by an exclamation mark (!) in front of a value.
    * A special key (GOAL) for the goal/target attribute. Its value is boolean.
    * A special key (|) for the OR operation. The value for that key is another
    dictionary/hypothesis, in a recursive structure."""
    if not examples:
        return h

    e = examples[0]
    if is_consistent(e, h):
        return current_best_learning(examples[1:], h, examples_so_far + [e])
    elif false_positive(e, h):
        for h2 in specializations(examples_so_far + [e], h):
            h3 = current_best_learning(examples[1:], h2, examples_so_far + [e])
            if h3 != 'FAIL':
                return h3
    elif false_negative(e, h):
        for h2 in generalizations(examples_so_far + [e], h):
            h3 = current_best_learning(examples[1:], h2, examples_so_far + [e])
            if h3 != 'FAIL':
                return h3

    return 'FAIL'


def specializations(examples_so_far, h):
    """Specialize the hypothesis. First add AND operations, then
    recursively specialize in the OR part of the hypothesis."""
    hypotheses = []

    # Add AND operations
    for e in examples_so_far:
        mod = ''
        if not e['GOAL']:
            mod = '!'

        for k, v in e.items():
            if k in h or k == 'GOAL' or k == '|':
                continue

            h2 = h.copy()
            h2[k] = mod + v
            if check_all_consistency(examples_so_far, h2):
                hypotheses += [h2]


    # Specialize in OR
    if '|' in h.keys():
        for h_or in specializations(examples_so_far, h['|']):
            h2 = h.copy()
            h2['|'] = h_or
            hypotheses += [h2]

    shuffle(hypotheses)
    return hypotheses


def generalizations(examples_so_far, h):
    """Generalize the hypothesis. First delete operations (including OR) from
    the hypothesis. Then, add OR operations if one doesn't already exist.
    If an OR operation exists, recursively generalize in that."""
    hypotheses = []
    h_powerset = powerset(h.keys())

    # Delete operations
    for deletions in h_powerset:
        h2 = h.copy()
        for d in deletions:
            del h2[d]

        if check_all_consistency(examples_so_far, h2):
            hypotheses += [h2]

    if '|' not in h:
        # Add OR
        hypotheses.extend(add_or(examples_so_far, h))
    else:
        # Generalize in OR
        for h_or in generalizations(examples_so_far, h['|']):
            if check_negative_consistency(examples_so_far, h2):
                h2 = h.copy()
                h2['|'] = h_or
                hypotheses += [h2]

    shuffle(hypotheses)
    return hypotheses


def add_or(examples_so_far, h):
    """Adds an OR operation to the hypothesis. The AND operations inside the OR
    are generated by the last example (which is the problematic one). Note that
    the function adds just one OR operation."""
    hypotheses = []
    e = examples_so_far[-1]
    mod = '!'
    if e['GOAL']:
        mod = ''

    attrs = {k: mod + v for k, v in e.items() if k != 'GOAL'}
    a_powerset = powerset(attrs.keys())

    for c in a_powerset:
        h2 = {}
        for k in c:
            h2[k] = attrs[k]

        if check_negative_consistency(examples_so_far, h2):
            h3 = h.copy()
            h3['|'] = h2
            hypotheses += [h3]

    return hypotheses


def check_all_consistency(examples, h):
    for e in examples:
        if not is_consistent(e, h):
            return False

    return True


def check_negative_consistency(examples, h):
    """Check if the negative examples are consistent under h."""
    for e in examples:
        if e['GOAL']:
            continue

        if not is_consistent(e, h):
            return False

    return True


def guess_value(e, h):
    """Guess value of example e under hypothesis h."""
    for k, v in h.items():
        if k == '|':
            if guess_value(e, v):
                return True
            continue

        if v[0] == '!':
            # v is a NOT expression
            # e[k], thus, should not be equal to v
            if e[k] == v[1:]:
                if '|' not in h:
                    return False
                else:
                    return guess_value(e, h['|'])
        elif e[k] != v:
            if '|' not in h:
                return False
            else:
                return guess_value(e, h['|'])

    return True


def is_consistent(e, h):
    return e["GOAL"] == guess_value(e, h)


def false_positive(e, h):
    if e["GOAL"] == False:
        if guess_value(e, h):
            return True

    return False


def false_negative(e, h):
    if e["GOAL"] == True:
        if not guess_value(e, h):
            return True

    return False
