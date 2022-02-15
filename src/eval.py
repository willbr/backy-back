import operator
import sys
import argparse
import fileinput

from functools import reduce

# from rich import print
from rich.console import Console
from ie.src.py.parse2_syntax import is_atom, puts_expr, remove_markers
from ie.src.py.ie import parse_file, parse_lines

console = Console(markup=False)
python_print = print
print = console.print

infix_symbols = "+ - * / =".split()


def transform_syntax(x):
    # print(f"transform_syntax: {x=}")
    head, *args = x
    # print(f"{args=}")
    # print(f"{args[0]=}")

    if head == 'ie/prefix':
        return args
    elif head == 'ie/infix':
        return transform_infix(args)
    elif head == 'ie/postfix':
        return [x[-1]] +  x[1:-1]
    elif head == 'ie/neoteric':
        return x[1:]
    elif args and str(args[0]) in infix_symbols:
        return transform_infix(x)
    else:
        return x


def eval(env, x):
    stack = env['stack']
    # print(f'eval start: {stack=}')
    # print(f'{x=}')
    # print()

    if is_atom(x):
        xx = x
    else:
        xx = transform_syntax(x)
    # print(f'{xx=}')

    if is_atom(xx):
        t = type(xx)

        if t is Symbol:
            if xx != symbol('$'):
                stack.append(env[str(xx)])
        else:
            stack.append(xx)

        return

    if x == []:
        return

    head, *args = xx
    s = str(head)

    # special forms
    if s == 'fn':
        fn_name, *fn_body = args
        env[str(fn_name)] = fn_body

    elif s == 'quote':
        if len(args) != 1:
            raise SyntaxError(f"quote only takes one argument: {repr(x)}")
        stack.append(args[0])
    elif s == 'if':
        assert False
    elif s == '=':
        lhs, rhs = args
        assert type(lhs) == Symbol
        env[str(lhs)] = rhs
    elif s == 'dup':
        stack.append(stack[-1])
    elif s == '.s':
        print(env['stack'])
    elif s == 'comment':
        pass
    elif s == '$':
        pass
    else:
        eval_list(env, args)
        apply(env, head, len(args))

    # print(f'eval end: {stack=}')
    # print()


def eval_list(env, args):
    for x in args:
        eval(env, x)


def apply(env, fn_name, num_args):
    # print(f"{env=}")
    # print(f"{stack=}")
    # print(f"{fn_name=}")
    # print()

    stack = env['stack']

    assert type(fn_name) == Symbol
    if (fn := env.get(str(fn_name), None)) is None:
        print(env)
        raise ValueError(f"unknown function: '{fn_name}'")
    # print(fn_spec)

    # print(callable(fn))
    # print(fn)
    # print(fn(1,2))

    if callable(fn):
        if num_args > 0:
            args = stack[-num_args:]
            del stack[-num_args:]
        else:
            args = []

        # print(f"{num_args=}")
        # print(f"{args=}")

        if str(fn_name) in infix_symbols:
            rval = reduce(fn, args)
        else:
            rval = fn(*args)

        # print(rval)
        # print(repeat)
        if rval:
            # print(f"{rval=}")
            stack.append(rval)
    else:
        for x in fn:
            eval(env, x)


def transform_infix(x):
    if len(x) == 1:
        return x[0]
    first_arg, first_op, *rest = x
    xx = [first_op, first_arg]
    for i in range(2, len(x)):
        if i % 2:
            assert first_op == x[i]
        else:
            xx.append(x[i])
    return xx


def repl(env, stack):
    stdin = fileinput.input()
    prompt = "\n; "
    while True:
        try:
            print(prompt, end="", flush=True)
            line = next(stdin)

            try:
                eval_lines(env, stack, [line])
                print('stack:', stack)
            except ValueError as e:
                print('error:', e)
            except SyntaxError as e:
                print('error:', e)

        except StopIteration:
            sys.exit(0)


def eval_lines(env, lines):
    prog = parse_lines(lines)
    eval_prog(env, prog)


def eval_prog(env, prog):
    prog = remove_markers2(prog, [symbol('ie/newline')])
    for x in prog:
        eval(env, x)


class Enviroment(dict):
    def __init__(self):
        super().__init__()

    def __getitem__(self, key):
        return super().__getitem__(key)


class Symbol(str):
    def __repr__(self):
        return self

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        h = str(id(self)) + "_" + self
        return hash(h)


symbols = {}


def symbol(s):
    # print(f"{s=}")
    # print(f"{symbols=}")
    if s not in symbols:
        symbols[s] = Symbol(s)
    return symbols[s]


def promote(t):
    try:
        return int(t)
    except:
        pass

    try:
        return float(t)
    except:
        pass

    if t[0] == '"':
        assert t[-1] == '"'
        return t[1:-1]

    return symbol(t)


def remove_markers2(prog, markers=['ie/newline', 'ie/backslash']):
    if is_atom(prog):
        return prog

    return [remove_markers2(x, markers) for x in prog if x not in markers]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", type=str)
    args = parser.parse_args()

    env = Enviroment()
    env['stack'] = []

    env['+'] = operator.add
    env['-'] = operator.sub
    env['*'] = operator.mul
    env['/'] = operator.truediv
    env['puts'] = print

    env['$'] = symbol('$')

    # elif fn == '.s':
        # print(stack)
        # return
    # elif fn == '.':
        # print(stack.pop())
        # return

    if args.file == []:
        if sys.stdin.isatty():
            try:
                repl(env)
            except KeyboardInterrupt:
                pass
            sys.exit()
        else:
            args.file.append("-")


    for file in args.file:
        prog = parse_file(file, promote)
        # print(remove_markers2(prog))
        eval_prog(env, prog)

