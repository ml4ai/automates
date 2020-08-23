import re
from string import ascii_uppercase
from collections import defaultdict
from typing import Union

from sympy.parsing.latex import parse_latex, LaTeXParsingError

from automates.equation_reading.latex_tokenizer import LatexTokenizer, Token


RESERVED_WORDS = {
    "_max",
    "_min",
    "_frac",
    "_dfrac",
    "_exp",
    "_sin",
    "_cos",
    "_tan",
    "_arctan",
    "_arccos",
    "_arcsin",
    "_ln",
}

safe_names = list(ascii_uppercase)


def tex2py(latex: str, include_sanitized: bool = False) -> Union[tuple, str]:
    tokens = list(sanitize(LatexTokenizer(latex)))
    sections = list(split_assignments(tokens))
    if len(sections) == 1:
        # TODO add lhs
        pass
    variables, spans = variable_dicts(tokens)
    new_tokens = list(replace_vars(tokens, variables, spans))
    new_latex = "".join(
        f"{t.value} " if t.code is None else t.value for t in new_tokens
    )
    try:
        python_eqn = repr(parse_latex(new_latex))
        for name, safe in variables.items():
            python_eqn = re.sub(rf"\b{safe}\b", name, python_eqn)
    except LaTeXParsingError as err:
        print(err)
        python_eqn = None

    if include_sanitized:
        return new_latex, python_eqn
    else:
        return python_eqn


def split_assignments(tokens):
    start = 0
    equals = Token("=", 11)
    try:
        while True:
            pos = tokens.index(equals, start)
            yield tokens[start:pos]
            start = pos + 1
    except ValueError:
        if start == 0:
            # if i haven't yielded then return everything in a chunk
            yield tokens


def sanitize(tokens):
    tokens = list(tokens)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.value in ["\\left", "\\right"]:
            pass
        elif t.value == "~":
            yield Token(" ", 10)
        else:
            yield t
        i += 1


def replace_vars(tokens, variable_names, variable_spans):
    i = 0
    while i < len(tokens):
        found = False
        for name in variable_names:
            for (start, stop) in variable_spans[name]:
                if i == start:
                    yield Token(variable_names[name], 11)
                    i = stop
                    found = True
                    break
            if found:
                break
        if not found:
            yield tokens[i]
            i += 1


def variable_dicts(tokens):
    variables = dict()
    spans = defaultdict(list)
    i = 0
    for chunk, start, stop in collect_chunks(tokens):
        name = "".join(c.value for c in chunk)
        name = re.sub(r"[^\w.]", "_", name)
        if name not in RESERVED_WORDS and name != "":
            variables[name] = safe_names[i]
            i += 1
            spans[name].append((start, stop))
    # variables: Dict[String, String]
    # spans: Dict[String, List[(Int, Int)]
    return variables, spans


def collect_chunks(tokens):
    state = "B"  # B(begin)  I(inside)
    start = 0
    chunk = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        i += 1
        if t.value.isalnum() or t.code is None or t.value == '.':
            # letter or control sequence
            if state == "B":
                state = "I"
                start = i - 1
            chunk.append(t)
        elif state == "I" and (t.code == 7 or t.code == 8 or t.value == '.'):
            group, j = get_group(tokens, i)
            if not is_number(group):
                i = j
                chunk.append(t)
                chunk.extend(group)
        else:
            yield (chunk, start, start + len(chunk))
            chunk = []
            state = "B"
    if len(chunk) > 0:
        yield (chunk, start, start + len(chunk))


def is_number(tokens):
    if len(tokens) > 1: # if we are in a group
        tokens = tokens[1:-1]
    for t in tokens:
        if not t.value.isdigit() and t.value != '.':
            return False
    return True


def get_group(tokens, pos):
    t = tokens[pos]
    if t.value.isalnum() or t.code is None:
        return ([t], pos + 1)
    elif t.code == 1:
        group = []
        while t.code != 2:
            group.append(t)
            pos += 1
            t = tokens[pos]
        group.append(t)
        return (group, pos + 1)


if __name__ == "__main__":

    latex = r"x = \frac{\sigma^2}{\tau} + b"
    print(tex2py(latex))
