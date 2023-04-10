import sys
import operator

from .parse import (
        parse_file,
        tree_values,
        Token,
        )

from .eval import (
        evalbb,
        )


from rich.console import Console
from rich.traceback import install

install(show_locals=True)

console = Console(markup=False)
python_print = print
print = console.print


def binaryop(fn):
    def opfn(x, y):
        if isinstance(x, Token):
            x = x.value
        if isinstance(y, Token):
            y = y.value
        return fn(x, y)
    return opfn


def main():
    args = sys.argv[1:]
    stack = []
    env = {
            'stack': stack,
            '+' : binaryop(operator.add),
            'puts' : print,
            }

    for filename in args:
        ast = parse_file(filename)
        for x in ast:
            print(tree_values(x))
            evalbb(env, x)
            print(('stack', env['stack']))
            print()

if __name__ == '__main__':
    main()
