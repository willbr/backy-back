import sys
from .parse import (
        parse_file,
        parse_string,
        tree_values,
        Token,
        strip_newlines,
        split_on_newline
        )

from rich.console import Console
from rich.traceback import install

install(show_locals=True)

console = Console(markup=False)
python_print = print
print = console.print

args = sys.argv[1:]


for filename in args:
    ast = parse_file(filename)
    for x in ast:
        xx = strip_newlines(x)
        if xx:
            print(tree_values(x))
            lhs, rhs = split_on_newline(x)
            print((tree_values(lhs), tree_values(rhs)))


