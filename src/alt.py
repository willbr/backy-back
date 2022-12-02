from rich.traceback import install
from rich.console import Console

console = Console(markup=False)
python_print = print
print = console.print

install(show_locals=True)

####################################

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

def main():
    while True:
        x = read_expr()
        if x == None:
            assert pending_line == None
            break
        print(x)
        print()

if __name__ == '__main__':
    print("hi")
    main()
    print("bye")

