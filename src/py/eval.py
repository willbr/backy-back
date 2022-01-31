import operator
import sys
from parse2_syntax import is_atom, puts_expr, remove_newline
from ie import parse_ie

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


if __name__ == "__main__":
    filename = sys.argv[1]
    prog = parse_ie(filename)
    prog = remove_newline(prog)

    for x in prog:
        print('x:', x)
        eval(env, x)


