import operator
import sys
import argparse
import fileinput

from rich import print
from ie.src.py.parse2_syntax import is_atom, puts_expr, remove_markers
from ie.src.py.ie import parse_file, parse_lines

infix_symbols = "+ - * /".split()


def transform_syntax(x):
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


def eval(env, stack, x):
    # print(f'{stack=}')
    # print(f'{x=}')
    # print()

    if is_atom(x):
        try:
            x = int(x)
        except:
            pass
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
        return
    elif head == 'if':
        assert False
    else:
        apply(env, stack, head, args)


def apply(env, stack, fn, args):
    # print(f"{env=}")
    # print(f"{stack=}")
    # print(f"{fn=}")
    # print(f"{args=}")
    # print()

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
        assert args == []
        print(stack)
        return
    elif fn == '.':
        assert args == []
        print(stack.pop())
        return
    else:
        if (fn_spec := env.get(fn, None)) is None:
            raise ValueError(f"unknown function: '{fn}'")

    if fn in infix_symbols:
        repeat = len(args) - 1
    else:
        if fn_spec[0] == 'builtin':
            _, fn, num_args = fn_spec
            if num_args != len(args):
                raise ValueError('wrong number of args', num_args, args)
        repeat = 1

    for x in args:
        eval(env, stack, x)

    if fn_spec[0] == 'builtin':
        _, fn, num_args = fn_spec

        for i in range(repeat):
            if len(stack) < num_args:
                raise ValueError(f"arguments missing form stack")

            args = stack[-num_args:]
            del stack[-num_args:]
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


def repl():
    stdin = fileinput.input()
    prompt = "\n; "
    while True:
        try:
            print(prompt, end="", flush=True)
            line = next(stdin)

            try:
                eval_lines(env, [line])
                print('stack:', stack)
            except ValueError as e:
                print('error:', e)
            except SyntaxError as e:
                print('error:', e)

        except StopIteration:
            sys.exit(0)


def eval_lines(env, lines):
    prog = parse_lines(lines)
    eval_prog(prog)


def eval_prog(prog):
    env = {}
    stack = []

    prog = remove_markers(prog)
    for x in prog:
        # print(f'{x=}')
        eval(env, stack, x)
        # print(f'{stack=}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", type=str)
    args = parser.parse_args()

    if args.file == []:
        if sys.stdin.isatty():
            try:
                repl()
            except KeyboardInterrupt:
                pass
            sys.exit()
        else:
            args.file.append("-")


    for file in args.file:
        prog = parse_file(file)
        eval_prog(prog)

