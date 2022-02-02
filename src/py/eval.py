import operator
import sys
import argparse
import fileinput

from parse2_syntax import is_atom, puts_expr, remove_markers
from ie import parse_file, parse_lines

env = {}

stack = []


def eval(env, x):
    global stack

    if is_atom(x):
        try:
            x = int(x)
        except:
            pass
        stack.append(x)
        return

    head, *args = x

    if head == 'ie/infix':
        head, *args = transform_infix(args)
    elif head == 'ie/postfix':
        head, args = x[-1], x[1:-1]

    if head == 'fn':
        fn_name, *fn_body = args
        env[fn_name] = fn_body
        return
    elif head == '+':
        fn_spec = ('builtin', operator.add, 2)
    elif head == '-':
        fn_spec = ('builtin', operator.sub, 2)
    elif head == '*':
        fn_spec = ('builtin', operator.mul, 2)
    elif head == '/':
        fn_spec = ('builtin', operator.div, 2)
    elif head == 'puts':
        fn_spec = ('builtin', print, 1)
    elif head == '.':
        print(stack.pop(0))
        return
    else:
        if (fn_spec := env.get(head, None)) is None:
            raise ValueError(f"unknown function: '{head}'")

    for y in args:
        eval(env, y)

    if fn_spec[0] == 'builtin':
        _, fn, num_args = fn_spec
        args = stack[-num_args:]
        stack = stack[:-num_args]
        rval = fn(*args)
        stack.append(rval)
    else:
        for z in fn_spec:
            eval(env, z)


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
    lines = []
    prompt = "; "
    while True:
        try:
            print(prompt, end="", flush=True)
            line = next(stdin)
            if line == '\n':
                eval_lines(env, lines)
                lines = []
                prompt = "; "
            else:
                prompt = "  "
            lines.append(line)

        except StopIteration:
            sys.exit(0)


def eval_lines(env, lines):
    prog = parse_lines(lines)
    eval_prog(prog)


def eval_prog(prog):
    prog = remove_markers(prog)
    for x in prog:
        #print('x:', x)
        eval(env, x)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", type=str)
    args = parser.parse_args()

    if args.file == []:
        if sys.stdin.isatty():
            repl()
            sys.exit()
        else:
            args.file.append("-")


    for file in args.file:
        prog = parse_file(file)
        eval_prog(prog)

