from rich import print
from rich.markup import escape
from pathlib import Path
from py.tokenise import tokenise_file
from py.parse1_indent import parse_indent
from py.parse2_syntax import parse_file, expr_to_string
from difflib import unified_diff


def read_file(fn):
    with open(fn) as f:
        return [l.strip('\n') for l in f.readlines()]


def read_indent(fn):
    tokens = tokenise_file(fn)
    tokens2 = parse_indent(tokens)
    return tokens2


def read_syntax(fn):
    ast = parse_file(fn)
    s = expr_to_string(ast)
    lines = s.split('\n')
    return lines


here = Path(__file__).parent

tokeniser_test_folders = list(here.glob("tests/tokeniser/*/*"))
parse1_indent_test_folders = list(here.glob("tests/parse1_indent/*/*"))
parse2_syntax_test_folders = list(here.glob("tests/parse2_syntax/*/*"))

specs = [
        (tokeniser_test_folders, tokenise_file),
        (parse1_indent_test_folders, read_indent),
        (parse2_syntax_test_folders, read_syntax),
        ]

for folders, reader in specs:
    for fld in folders:
        # print(repr(fld))

        in_file = fld.joinpath("in.txt")
        out_file = fld.joinpath("out.txt")

        if fld.stem.startswith("err-"):
            try:
                tokens = list(reader(in_file))
                print(fld)
                print(fld.stem)
                raise ValueError("test didn't fail")
            except:
                pass
        else:
            result = list(reader(in_file))
        # print(list(map(escape,result)))

        lines = read_file(out_file)
        # print(lines)
        if lines == []:
            with open(out_file, 'w') as f:
                f.write('\n'.join(result))

        diff = list(unified_diff(result, lines))
        if diff:
            print(repr(fld))
            print(result)
            print(lines)
            print(diff)
            print(repr(fld))
            exit(1)

