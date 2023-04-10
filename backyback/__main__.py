from rich.console import Console
from rich.traceback import install
from typing import NamedTuple
import itertools
import re

from itertools import tee, islice, chain


install(show_locals=True)

console = Console(markup=False)
python_print = print
print = console.print

def hline(n=1, c='#', width=60, title=None):
    print('\n'*n)
    if title:
        print(f' {title}')
    print(c*width)
    print('\n'*n)

def peek(iterable):
    a, b = tee(iterable)
    c = chain(islice(b, 1, None), [None])
    return zip(a, c)

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

def tokenize(code):
    code = code.strip()

    word_regex = r'[^ \t\n\"()]+'
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),
        ('NEOTERIC',   word_regex + r'\('),
        ('WORD',   word_regex),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('STRING',   r'"[^!]*"'),
        ('NEWLINE',  r'\n[ ]*'),
        ('SKIP',     r'[ ]+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    column = 1
    line_num = 1
    line_start = 0

    cur_indent = 0
    indent_width = 4

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'NEWLINE':
            yield Token(kind, value[0], line_num, column)
            line_start = mo.end()
            line_num += 1

            indent_chars = value[1:]
            indent = len(indent_chars) // indent_width
            delta = indent - cur_indent

            if delta > 1:
                assert False
            elif delta == 1:
                yield Token('INDENT', '', line_num, column)
            elif delta == 0:
                yield Token('NOINDENT', '', line_num, column)
            else:
                for i in range(0, delta, -1):
                    yield Token('DEDENT', '', line_num, column)

            cur_indent = indent

            continue
        elif kind == 'SKIP':
            continue
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        yield Token(kind, value, line_num, column)


def convert_indent_to_sexp(tokens):
    #breakpoint()
    depth = -1

    for token, next_token in peek(tokens):
        if token.type == 'INDENT':
            yield Token('LPAREN', '(', token.line, token.column)
            depth += 1
            continue
        elif token.type == 'NOINDENT':
            yield Token('RPAREN', ')', token.line, token.column)
            yield Token('LPAREN', '(', token.line, token.column)
            continue
        elif token.type == 'DEDENT':
            yield Token('RPAREN', ')', token.line, token.column)
            if next_token.type != 'DEDENT':
                yield Token('RPAREN', ')', token.line, token.column)
                yield Token('LPAREN', '(', token.line, token.column)
            depth -= 1
            continue
        elif depth == -1:
            yield Token('LPAREN', '(', token.line, token.column)
            depth = 1

        yield token

    for i in range(depth):
        yield Token('RPAREN', ')', token.line, token.column)


def parse_tree(tokens):
    x = []
    stack = [x]
    for t in tokens:
        if t.type == 'LPAREN':
            x = []
            stack.append(x)
        elif t.type == 'RPAREN':
            stack.pop()
            tos = stack[-1]
            if len(stack) == 1:
                yield x
            else:
                tos.append(x)
                x = tos
        else:
            x.append(t.value)

    assert len(stack) == 1
    tos = stack[0]
    assert len(tos) == 0



code = """
a b
    c
        d e
f
"""


if __name__ == '__main__':
    hline(5)

    if True:
        hline(title='# code')
        print(code)

    tokens = list(tokenize(code))
    if True:
        hline(title='# tokens')
        for token in tokens:
            #print(token)
            print(token.type, repr(token.value))

    tokens2 = list(convert_indent_to_sexp(tokens))
    if True:
        hline(title='# sexp')
        if False:
            for token in tokens2:
                print(token)

        print(' '.join(str(t.value) for t in tokens2 if t.type != 'NEWLINE'))
        print('( a b ( c ( d e ) ) ) ( f )')

    if True:
        hline(title='# tree')
        ast = parse_tree(tokens2)
        for expr in ast:
            print(expr)

