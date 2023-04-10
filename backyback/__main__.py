import sys
from .parse import (
        parse_file,
        parse_string,
        tree_values,
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
        print(tree_values(x))
