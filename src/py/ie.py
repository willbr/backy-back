import sys
from tokenise import tokenise_file, tokenise_lines
from parse1_indent import parse_indent
from parse2_syntax import parse_syntax
from pprint import pprint


def parse_file(filename):
    tokens  = tokenise_file(filename)
    tokens2 = parse_indent(tokens)
    ast     = parse_syntax(tokens2)
    return ast


def parse_lines(s):
    tokens  = tokenise_lines(s)
    tokens2 = parse_indent(tokens)
    ast     = parse_syntax(tokens2)
    return ast


if __name__ == "__main__":
    filename = sys.argv[1]
    ast = parse_file(filename)
    pprint(ast)

