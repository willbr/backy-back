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

    token_regex = '[^\s()]+[(\[]?'

    m = re.search(f'^(\n|\s+|[()[\],"]|{token_regex})', data_tail)
    if m is None:
        t = data_tail
        data_tail = ''
        assert False
        return t

    start = m.start()
    end = m.end()
    c = data_tail[start]

    if c == '"':
        t, data_tail = read_string(data_tail)
        return t

    d=data_tail
    t = data_tail[:end]
    assert t != '"'
    data_tail = data_tail[end:]
    return t
    assert False

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

def read_infix():
    infix_depth = 1
    tokens = []
    while True:
        t = next_token()
        assert t != None

        if t[0] == ' ':
            continue

        tokens.append(t)

        if t == '(':
            infix_depth += 1
        elif t == ')':
            infix_depth -= 1
            if infix_depth == 0:
                break
        elif t == ',':
            assert False

    return tokens

def parse_line(tokens):
    raise ValueError("What is an expr [cmd [args] [children]]???")
    assert False

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
    elif t[0] == '(':
        nfx = read_infix()
        assert False
    elif t[-1] == '(':
        nfx = read_infix()
        assert False
    else:
        tokens.append(t)

    while True:
        t = next_token()
        if t == None:
            break
        elif t[0] == ' ':
            continue
        elif t == '\n':
            break
        elif t[0] == '(':
            nfx = read_infix()
            assert False
        elif t[-1] == '(':
            cmd = t[:-1]
            nfx = read_infix()
            spec = ['neoteric', cmd, '(', *nfx]
            tokens.extend(spec)
        else:
            tokens.append(t)

    head, *tail = parse_line(tokens)
    line_spec = depth, [head, tail]
    return line_spec

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

def fn_add(wst, x):
    cmd, args, *children = x
    assert children == []
    for arg in args:
        eval(wst, arg)
    b = wst.pop()
    a = wst.pop()
    r = a + b
    wst.append(r)
    print(wst)

def fn_assign(wst, x):
    cmd, args, *children = x
    assert children == []
    dst, val = args
    eval(wst, val)
    xval = wst.pop()
    env[dst] = xval

def fn_print_stack(wst, x):
    cmd, args, *children = x
    assert args == []
    assert children == []
    print(f'stack: {wst}')

def fn_puts(wst, x):
    cmd, args, *children = x
    assert children == []
    assert len(args) == 1
    eval(wst, args[0])
    s = wst.pop()
    print(s)

def fn_define(wst, x):
    cmd, args, *children = x
    assert children != []
    name, *tail = args
    assert tail == []
    fn = ['lambda', [], children]
    nx = ['=', [name, fn]]
    fn_assign(wst, nx)

def fn_lambda(wst, x):
    cmd, args, children = x
    assert args == []
    assert children != []
    wst.append(x)

def fn_infix(wst, x):
    cmd, args, *children = x
    assert children == []
    if len(args) == 1:
        eval(args[0])
        return
    assert len(args) % 3 == 0
    assert False

def fn_dup(wst, x):
    cmd, args, *children = x
    assert args == []
    assert children == []
    tos = wst[-1]
    wst.append(tos)

def fn_neoteric(wst, x):
    assert False

env = {
        '+': fn_add,
        '=': fn_assign,
        '.s': fn_print_stack,
        'puts': fn_puts,
        'fn': fn_define,
        'neoteric': fn_neoteric,
        'lambda': fn_lambda,
        'infix': fn_infix,
        'dup': fn_dup,
        }

def eval(wst, x):
    if not isinstance(x, list):
        try:
            n = float(x)
            wst.append(n)
            return
        except ValueError:
            pass
        c = x[0]
        if c == '"':
            s = x[1:-1]
            wst.append(s)
            return
        elif x == '$':
            # do nothing
            return
        else:
            try:
                r = env[x]
                wst.append(r)
                return
            except KeyError as e:
                raise ValueError(f'unknown command: {repr(x)}')

    cmd, args, *children = x
    if type(cmd) is list:
        old_cmd = cmd
        cmd = eval(old_cmd)
        assert False
    else:
        fn = env.get(cmd, None)

    if fn == None:
        eval_infix(wst, *x)
    elif isinstance(fn, list):
        fn_cmd, fn_params, fn_children = fn
        assert fn_cmd == 'lambda'
        assert fn_params == []
        for child in fn_children:
            eval(wst, child)
    else:
        fn(wst, x)

def eval_infix(wst, line_cmd, line_args, children=None):
    assert children == [] or children == None
    x = [line_cmd]
    x.extend(line_args)
    nx = transform_infix(x)
    eval(wst, nx)

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
        print(x)
        print(global_stack)
        eval(global_stack, x)
        print(global_stack)
        print()

if __name__ == '__main__':
    main()

