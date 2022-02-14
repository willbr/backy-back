import operator
import sys
import argparse
import fileinput

from rich import print
from ie.src.py.parse2_syntax import is_atom, puts_expr, remove_markers
from ie.src.py.ie import parse_file, parse_lines

infix_symbols = "+ - * / =".split()


def transform_syntax(x):
    # print(x)
    head, *args = x

    if head == 'ie/prefix':
        return args
    elif head == 'ie/infix':
        return transform_infix(args)
    elif head == 'ie/postfix':
        return [x[-1]] +  x[1:-1]
    elif args and args[0] in infix_symbols:
        return transform_infix(x)
    else:
        return x


def eval(env, x):
    # print(f'{stack=}')
    # print(f'{x=}')
    # print()

    stack = env['stack']

    if is_atom(x):
        t = type(x)

        if t is Symbol:
            stack.append(env[x])
        else:
            stack.append(x)

        return

    if x == []:
        return

    head, *args = transform_syntax(x)

    # special forms
    if head == 'fn':
        fn_name, *fn_body = args
        env[fn_name] = fn_body

    elif head == 'quote':
        if len(args) != 1:
            raise SyntaxError(f"quote only takes one argument: {repr(x)}")
        stack.append(args[0])
    elif head == 'if':
        assert False
    elif head == '=':
        lhs, rhs = args
        env[lhs] = rhs
    else:
        eval_list(env, args)
        apply(env, head, len(args))


def eval_list(env, args):
    for x in args:
        eval(env, x)


def apply(env, fn, num_args):
    # print(f"{env=}")
    # print(f"{stack=}")
    # print(f"{fn=}")
    # print()

    stack = env['stack']

    if fn == '+':
        fn_spec = ('builtin', operator.add, 2)
    elif fn == '-':
        fn_spec = ('builtin', operator.sub, 2)
    elif fn == '*':
        fn_spec = ('builtin', operator.mul, 2)
    elif fn == '/':
        fn_spec = ('builtin', operator.truediv, 2)
    elif fn == 'puts':
        fn_spec = ('builtin', print, 1)
    elif fn == '.s':
        print(stack)
        return
    elif fn == '.':
        print(stack.pop())
        return
    else:
        if (fn_spec := env.get(fn, None)) is None:
            raise ValueError(f"unknown function: '{fn}'")

    if fn in infix_symbols:
        repeat = num_args - 1
    else:
        if fn_spec[0] == 'builtin':
            _, fn, num_params = fn_spec
            if num_params != num_args:
                raise ValueError(f'{num_params=} != {num_args=}')
        repeat = 1

    if fn_spec[0] == 'builtin':
        _, fn, num_params = fn_spec

        for i in range(repeat):
            if len(stack) < num_params:
                raise ValueError(f"arguments missing form stack")

            args = stack[-num_params:]
            del stack[-num_params:]
            rval  = fn(*args)
            if rval:
                stack.append(rval)
    else:
        for i in range(repeat):
            for z in fn_spec:
                eval(env, stack, z)


def transform_infix(x):
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
    prog = remove_markers(prog)
    for x in prog:
        # print(f'{x=}')
        eval(env, x)
        # print(f'{stack=}')


class Enviroment(dict):
    def __init__(self):
        super().__init__()

    def __getitem__(self, key):
        return super().__getitem__(key)


class Symbol(str):
    def __repr__(self):
        return self


symbols = {}


def symbol(s):
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
        assert False

    return symbol(t)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", type=str)
    args = parser.parse_args()

    env = Enviroment()
    env['stack'] = []

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
        print(prog)
        eval_prog(env, prog)

