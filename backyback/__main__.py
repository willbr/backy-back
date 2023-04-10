import sys
from .parse import (
        parse_file,
        tree_values,
        )

from rich.console import Console
from rich.traceback import install

install(show_locals=True)

console = Console(markup=False)
python_print = print
print = console.print

def main():
    args = sys.argv[1:]

    for filename in args:
        ast = parse_file(filename)
        for x in ast:
            print(tree_values(x))

if __name__ == '__main__':
    main()
