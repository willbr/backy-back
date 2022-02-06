from rich import print
from pathlib import Path
from py.tokenise import tokenise_file
from difflib import unified_diff

def read_file(fn):
    with open(fn) as f:
        return [l.strip('\n') for l in f.readlines()]


here = Path(__file__).parent

tokeniser_test_folders = list(here.glob("tests/tokeniser/*/*"))
parse1_indent_test_folders = list(here.glob("tests/parse1_indent/*/*"))
parse2_syntax_test_folders = list(here.glob("tests/parse2_syntax/*/*"))

specs = [
        (tokeniser_test_folders, tokenise_file),
        ]

for spec in specs:
    folders, reader = spec
    for fld in folders:
        # print(repr(fld))

        in_file = fld.joinpath("in.txt")
        out_file = fld.joinpath("out.txt")

        tokens = list(reader(in_file))
        # print(tokens)

        lines = read_file(out_file)
        # print(lines)
        if lines == []:
            with open(out_file, 'w') as f:
                f.write('\n'.join(tokens))

        diff = list(unified_diff(tokens, lines))
        if diff:
            print(repr(fld))
            print(tokens)
            print(lines)
            print(diff)
            print(repr(fld))
            exit(1)

