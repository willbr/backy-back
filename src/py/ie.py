import sys
from tokenise import read_tokens
from parse1_indent import parse_indent
from parse2_syntax import parse_syntax
from pprint import pprint


def parse_ie(filename):
    tokens  = read_tokens(filename)
    tokens2 = parse_indent(tokens)
    ast     = parse_syntax(tokens2)
    return ast


if __name__ == "__main__":
    filename = sys.argv[1]
    ast = parse_ie(filename)
    pprint(ast)

