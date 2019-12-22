import sys
from latex_tokenizer import *
from align_eq_bb import tokens_to_string

def normalize(tokens):
    tokens = list(tokens)
    i = 0
    while i < len(tokens):
        if tokens[i].value == r'\label':
            i = drop_group(tokens, i)
        elif i < len(tokens) - 1 and tokens[i].code == CategoryCode.StartOfGroup and tokens[i+1].value == r'\rm':
            yield Token(r'\mathrm', None)
            yield tokens[i]
            i += 2
        elif tokens[i].value == r'\rm' and tokens[i+1].code == CategoryCode.StartOfGroup:
            yield Token(r'\mathrm', None)
            yield tokens[i+1]
            i += 2
        elif tokens[i].code == CategoryCode.Subscript:
            yield tokens[i]
            i += 1
            j = drop_group(tokens, i)
            if i == j:
                yield Token('{', CategoryCode.StartOfGroup)
                yield tokens[i]
                yield Token('}', CategoryCode.EndOfGroup)
            else:
                for k in range(i, j+1):
                    yield tokens[k]
                i = j
            i += 1
        elif tokens[i].code == CategoryCode.Superscript:
            j = drop_group(tokens, i+1)
            if j+1 < len(tokens) and tokens[j+1].code == CategoryCode.Subscript:
                # flip and try again
                k = drop_group(tokens, j+2)
                tokens = tokens[:i] + tokens[j+1:k+1] + tokens[i:j+1] + tokens[k+1:]
                continue
            else:
                yield tokens[i]
                i += 1
                if i == j: 
                    yield Token('{', CategoryCode.StartOfGroup)
                    yield tokens[i]
                    yield Token('}', CategoryCode.EndOfGroup)
                else:
                    for k in range(i, j+1):
                        yield tokens[k]
                    i = j
                i += 1
        else:
            yield tokens[i]
            i += 1


def get_group(tokens, i):
    j = drop_group(tokens, i)
    return tokens[i:j+1]

def drop_group(tokens, i):
    j = i
    n_starts = n_ends = 0
    while j < len(tokens):
        tok = tokens[j]
        if tok.code == CategoryCode.StartOfGroup:
            n_starts += 1
        elif tok.code == CategoryCode.EndOfGroup:
            n_ends += 1
        if n_starts == n_ends:
            # either we completed the group or there was never one
            return j
        elif n_starts > n_ends:
            # keep going
            j += 1
        elif n_starts < n_ends:
            # invalid group
            return i


def render(formula):
    for t in normalize(LatexTokenizer(formula)):
        if t.code in (CategoryCode.Letter, CategoryCode.Space, CategoryCode.Other):
            yield t.value

if __name__ == '__main__':
    command = sys.argv[1]
    formula = sys.argv[2]
    if command == 'normalize':
        print(tokens_to_string(normalize(LatexTokenizer(formula))))
    elif command == 'render':
        for t in normalize(LatexTokenizer(formula)):
            if t.code in (CategoryCode.Letter, CategoryCode.Space, CategoryCode.Other):
                print(t.value, end='')
        print()
