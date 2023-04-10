import operator
import sys
import argparse
import fileinput

from functools import reduce
from .parse import (
        is_atom,
        Token,
        strip_newlines,
        tree_values,
        )

# from rich import print
from rich.console import Console

console = Console(markup=False)
python_print = print
print = console.print

def evalbb(env, x):
    stack = env['stack']

    if is_atom(x):
        stack.append(x)
        return

    if x == []:
        return

    head, *args = x
    assert head.type == 'WORD'
    s = head.value

    # special forms
    if s == 'fn':
        assert False
        fn_name, *fn_body = args
        env[fn_name.value] = fn_body

    elif s == 'quote':
        if len(args) != 1:
            raise SyntaxError(f"quote only takes one argument: {repr(x)}")
        stack.append(args[0])
    elif s == 'if':
        assert False
    elif s == '=':
        lhs, rhs = args
        env[lhs.value] = rhs
    elif s == 'dup':
        stack.append(stack[-1])
    elif s == '.s':
        print(env['stack'])
    elif s == 'comment':
        pass
    elif s == '$':
        pass
    elif s == 'infix':
        ix = transform_infix(args)
        evalbb(env, ix)
        return 
    elif s == 'neo-infix':
        name, *iargs = args
        ix = transform_infix(iargs)
        new_x = [name, ix]
        evalbb(env, new_x)
        assert False

    else:
        evalbb_list(env, args)
        apply(env, head, len(args))

    # print(f'eval end: {stack=}')
    # print()


def evalbb_list(env, args):
    for x in args:
        evalbb(env, x)


def apply(env, fn_name, num_args):
    stack = env['stack']

    #print(f"{env=}")
    #print(f"{stack=}")
    #print(f"{fn_name=}")
    #print(f"{num_args=}")
    #print()

    assert isinstance(fn_name, Token)
    assert fn_name.type == 'WORD'

    if (fn := env.get(fn_name.value, None)) is None:
        print(env)
        raise ValueError(f"unknown function: '{fn_name.value}'")
    # print(fn_spec)

    # print(callable(fn))
    # print(fn)
    # print(fn(1,2))

    assert callable(fn)

    if num_args > 0:
        args = stack[-num_args:]
        del stack[-num_args:]
    else:
        args = []

    #print(f"{num_args=}")
    #print(f"{args=}")

    rval = fn(*args)

    # print(rval)
    # print(repeat)
    if rval:
        # print(f"{rval=}")
        stack.append(rval)


def transform_infix(x):
    """
    transform infix to prefix

    (1 + 2 + 3)
    [+ [+ 1 2] 3]
    {1 2 + 3 +}

    (1 + 2 + 3 + 4)
    [+ [+ [+ 1 2] 3] 4]
    {1 2 + 3 + 4 +}
    """
    x = strip_newlines(x)

    if len(x) == 1:
        return x[0]
    assert len(x) > 2
    first_arg, first_op, second_arg, *rest = x
    assert first_op.type == 'WORD'
    xx = [first_op, first_arg, second_arg]
    for i in range(3, len(x)):
        if i % 2:
            assert first_op.value == x[i].value
        else:
            xx = [first_op, xx, x[i]]
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", type=str)
    args = parser.parse_args()

    env = {}
    env['stack'] = []

    env['+'] = operator.add
    env['-'] = operator.sub
    env['*'] = operator.mul
    env['/'] = operator.truediv
    env['puts'] = print

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
        # print(remove_markers(prog))
        eval_prog(env, prog)

