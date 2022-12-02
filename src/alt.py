from rich.traceback import install
from rich.console import Console

console = Console(markup=False)
python_print = print
print = console.print

install(show_locals=True)

####################################
from functools import reduce

import operator as op
import sys
import re
#print('hi')
filename = sys.argv[1]

i = 0
with open(filename) as f:
    data = f.read()

data_tail = data
pending_token = None
pending_line = None
global_stack = []

def read_string(s):
    m = re.search('"', s[1:])
    end = m.end()+ 1
    string = s[:end]
    tail = s[end:]
    return string, tail

def push_token(t):
    global pending_token
    assert pending_token == None
    pending_token = t

def peek_token():
    global pending_token
    if pending_token == None:
        pending_token = next_token()
    return pending_token

def next_token():
    global data_tail
    global pending_token

    if pending_token:
        t = pending_token
        pending_token = None
        return t

    if data_tail == '':
        return None
    m = re.search('\n|\s+|[(),"]', data_tail)
    if m == None:
        t = data_tail
        data_tail = ''
        return t

    start = m.start()
    end = m.end()
    c = data_tail[start]

    if start == 0:
        if c == '"':
            t, data_tail = read_string(data_tail)
        else:
            t = data_tail[:end]
            data_tail = data_tail[end:]
        return t

    t = data_tail[:start]
    data_tail = data_tail[start:]
    return t

def read_tokens():
    global data_tail
    tokens = []
    while True:
        t = next_token()

        if t == None:
            break

        tokens.append(t)
    return tokens

def calc_depth(s):
    #print(repr(s))
    l = len(s)
    assert l % 4 == 0
    depth = l // 4
    return depth

def chomp_empty_lines():
    nt = peek_token()
    while nt == '\n':
        _ = next_token()
        nt = peek_token()

def push_line(depth, tokens):
    global pending_line
    assert pending_line == None
    pending_line = (depth, tokens)

def read_line():
    global pending_line
    if pending_line != None:
        depth, tokens = pending_line
        pending_line = None
        return depth, tokens

    chomp_empty_lines()

    t = next_token()
    tokens = []
    depth = 0

    if t == None:
        return depth, None
    elif t[0] == ' ':
        depth = calc_depth(t)
    else:
        tokens.append(t)

    while True:
        t = next_token()
        if t == None:
            break
        elif t[0] == (' '):
            continue
        elif t == '\n':
            break

        tokens.append(t)

    head, *tail = tokens
    return depth, [head, tail]

def unwind(stack):
    children = stack.pop()
    tos = stack[-1]
    parent = tos[-1]
    parent.extend(children)

def read_expr():
    cur_indent = 0

    this_indent, body = read_line()
    assert this_indent == 0

    if body == None:
        return None

    stack = [[body]]
    #print('stack', str(stack))

    while True:
        #print('stack', str(stack))
        this_indent, body = read_line()
        #print(this_indent, str(body))

        if body == None:
            break
        elif this_indent == 0:
            push_line(this_indent, body)
            break

        if this_indent > cur_indent + 1:
            assert False
        elif this_indent == cur_indent + 1:
            stack.append([body])
        elif this_indent == cur_indent:
            tos = stack[-1]
            tos.append(body)
        else:
            i = this_indent
            while i < cur_indent:
                unwind(stack)
                i += 1
            tos = stack[-1]
            tos.append(body)

        cur_indent = this_indent

    #print(f'{this_indent=} {cur_indent=}')

    while cur_indent > 0:
        unwind(stack)
        cur_indent -= 1

    #print(stack)
    assert len(stack) == 1
    assert len(stack[0]) == 1
    return stack[0][0]

def pretty(tree, depth = 0):
    #print(f'{tree=}')
    indent = '    ' * depth
    for expr in tree:
        #print(f'{expr=}')
        if len(expr) == 1:
            head = expr[0]
            tail = None
        else:
            head, tail = expr
        s = ' '.join(head)
        print(f'{indent}{s}')
        if tail:
            pretty(tail, depth + 1)

def fn_add(x):
    cmd, args, *children = x
    assert children == []
    xargs = list(map(eval, args))
    r = reduce(op.add, xargs)
    return r

def fn_assign(x):
    cmd, args, *children = x
    assert children == []
    dst, val = args
    xval = eval(val)
    env[dst] = xval

def fn_print_stack(x):
    cmd, args, *children = x
    assert args == []
    assert children == []
    print(f'stack: {global_stack}')

def fn_puts(x):
    cmd, args, *children = x
    assert children == []
    assert len(args) == 1
    xarg = eval(args[0])
    print(xarg)

def fn_define(x):
    cmd, args, *children = x
    assert children != []
    name, *tail = args
    assert tail == []
    fn = ['lambda', [], children]
    nx = ['=', [name, fn]]
    fn_assign(nx)
    return fn

def fn_lambda(x):
    cmd, args, *children = x
    assert args == []
    assert children != []
    return x

env = {
        '+': fn_add,
        '=': fn_assign,
        '.s': fn_print_stack,
        'puts': fn_puts,
        'fn': fn_define,
        'lambda': fn_lambda,
        }

def eval(x):
    if not isinstance(x, list):
        try:
            n = float(x)
            return n
        except ValueError:
            pass
        c = x[0]
        if c == '"':
            s = x[1:-1]
            return s
        else:
            r = env[x]
            return r

    cmd, args, *children = x
    if type(cmd) is list:
        old_cmd = cmd
        cmd = eval(old_cmd)
        assert False
    else:
        fn = env.get(cmd, None)

    if fn == None:
        r = eval_infix(x)
    else:
        #print(x)
        r = fn(x)
        #print()
    return r

def eval_infix(line):
    line_cmd, line_args, *children = line
    assert children == []
    x = [line_cmd]
    x.extend(line_args)
    nx = transform_infix(x)
    r = eval(nx)
    return r

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
    if len(x) == 1:
        return x[0]
    assert len(x) > 2
    first_arg, first_op, second_arg, *rest = x
    xx = [first_op, [first_arg, second_arg]]
    for i in range(3, len(x)):
        if i % 2:
            assert first_op == x[i]
        else:
            xx = [first_op, [xx, x[i]]]
    return xx

def main():
    while True:
        x = read_expr()
        if x == None:
            assert pending_line == None
            break
        r = eval(x)
        global_stack.append(r)

if __name__ == '__main__':
    main()

