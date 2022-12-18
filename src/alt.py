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

class Reader():
    def __init__(self, filename=None):
        self.i = 0
        self.data = None
        self.data_tail = None
        self.pending_token = None
        self.pending_line = None

        if filename != None:
            self.read_from_file(filename)

    def read_from_file(self, filename):
        with open(filename) as f:
            data = f.read()
        self.read_from_string(data)

    def read_from_string(self, s):
        self.i = 0
        self.data = s
        self.data_tail = s

    def read_tokens(self):
        while True:
            t = self.next_token()
            if t is None:
                break
            yield t

    def read_expr(self):
        cur_indent = 0

        this_indent, body = self.read_line()
        assert this_indent == 0

        if body == None:
            return None

        stack = [[body]]
        #print('stack', str(stack))

        while True:
            #print('stack', str(stack))
            this_indent, body = self.read_line()
            #print(this_indent, str(body))

            if body == None:
                break
            elif this_indent == 0:
                self.push_line(this_indent, body)
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

    def read_line(self):
        if self.pending_line != None:
            depth, tokens = self.pending_line
            self.pending_line = None
            return depth, tokens

        self.chomp_empty_lines()

        t = self.next_token()
        tokens = []
        depth = 0

        if t == None:
            return depth, None
        elif t[0] == ' ':
            depth = calc_depth(t)
        elif t[0] == '(':
            nfx = self.read_infix()
            assert False
        elif t[-1] == '(':
            nfx = self.read_infix()
            assert False
        else:
            tokens.append(t)

        while True:
            t = self.next_token()
            if t == None:
                break
            elif t[0] == ' ':
                continue
            elif t == '\n':
                break
            elif t[0] == '(':
                nfx = self.read_infix()
                tokens.append(nfx)
            elif t[-1] == '(':
                cmd = t[:-1]
                nfx = self.read_infix()
                spec = [cmd, nfx]
                tokens.append(spec)
            else:
                tokens.append(t)

        head, *tail = tokens
        line_spec = depth, [head, tail]
        return line_spec

    def chomp_empty_lines(self):
        nt = self.peek_token()
        while nt == '\n':
            _ = self.next_token()
            nt = self.peek_token()

    def peek_token(self):
        if self.pending_token == None:
            self.pending_token = self.next_token()
        return self.pending_token

    def next_token(self):
        if self.pending_token:
            t = self.pending_token
            self.pending_token = None
            return t

        if self.data_tail == '':
            return None

        token_regex = '[^\s(),]+[(\[]?'

        m = re.search(f'^(\n|\s+|[()[\],"]|{token_regex})', self.data_tail)
        if m is None:
            t = self.data_tail
            self.data_tail = ''
            assert False
            return t

        start = m.start()
        end = m.end()
        c = self.data_tail[start]

        if c == '"':
            t, self.data_tail = read_string(self.data_tail)
            return t

        t = self.data_tail[:end]
        assert t != '"'
        self.data_tail = self.data_tail[end:]
        return t

    def push_line(self, depth, tokens):
        assert self.pending_line == None
        self.pending_line = (depth, tokens)

    def read_infix(self):
        infix_depth = 1
        x = []
        top = [x]
        while True:
            t = self.next_token()
            assert t != None

            if t[0] == ' ':
                continue

            if t == '(':
                child = self.read_infix()
                assert False
            elif t == ')':
                break
            elif t == ',':
                x = []
                top.append(x)
            else:
                x.append(t)

        px = list(map(transform_infix, top))
        if len(px) == 1:
            return px[0]
        else:
            assert False

global_stack = []

def read_string(s):
    m = re.search('"', s[1:])
    end = m.end()+ 1
    string = s[:end]
    tail = s[end:]
    return string, tail

def calc_depth(s):
    #print(repr(s))
    l = len(s)
    assert l % 4 == 0
    depth = l // 4
    return depth

def unwind(stack):
    children = stack.pop()
    tos = stack[-1]
    parent = tos[-1]
    parent.extend(children)

def fn_add(wst, x):
    cmd, args, children = split_expr(x)
    assert children == []
    for arg in args:
        eval(wst, arg)
    b = wst.pop()
    a = wst.pop()
    r = a + b
    wst.append(r)
    #print(wst)

def fn_assign(wst, x):
    cmd, args, children = split_expr(x)
    if len(args) == 2:
        assert children == []
        dst, val = args
    elif len(args) == 1:
        dst = args[0]
        val = children
        assert False
    else:
        assert False
    eval(wst, val)
    xval = wst.pop()
    env[dst] = xval

def fn_print_stack(wst, x):
    cmd, args, children = split_expr(x)
    assert args == []
    assert children == []
    print(f'stack: {wst}')

def fn_puts(wst, x):
    cmd, args, children = split_expr(x)
    assert children == []
    if args:
        assert len(args) == 1
        eval(wst, args[0])
    s = wst.pop()
    print(s)

def fn_lambda(wst, x):
    cmd, args, children = split_expr(x)
    assert args == []
    assert children != []
    wst.append(x)

def fn_dup(wst, x):
    cmd, args, children = split_expr(x)
    assert args == []
    assert children == []
    tos = wst[-1]
    wst.append(tos)

def fn_newline(wst, x):
    cmd, args, children = split_expr(x)
    assert args == []
    assert children == []

def fn_define_function(wst, x):
    cmd, args, children = split_expr(x)
    assert cmd == 'fn'
    assert len(args) == 1
    fn_name = args[0]
    assert children != []
    env[fn_name] = ['lambda', *children]

env = {
        '+': fn_add,
        '=': fn_assign,
        '.s': fn_print_stack,
        'puts': fn_puts,
        'lambda': fn_lambda,
        'dup': fn_dup,
        '\n': fn_newline,
        'fn': fn_define_function,
        }

def split_expr(x):
    try:
        i = x.index('\n')
        cmd, *args = x[:i]
        children = x[i+1:]
    except ValueError:
        cmd, *args = x
        children = []
    return cmd, args, children

def eval(wst, x):
    print()
    print('eval', repr(x))
    print('wst', repr(wst))

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

    cmd, args, children = split_expr(x)
    if type(cmd) is list:
        old_cmd = cmd
        cmd = eval(old_cmd)
        assert False
    else:
        fn = env.get(cmd, None)

    if fn == None:
        eval_infix(wst, x)
    elif isinstance(fn, list):
        fn_cmd, *fn_children = fn
        for arg in args:
            eval(wst, arg)
        assert fn_cmd == 'lambda'
        for child in fn_children:
            eval(wst, child)
    else:
        fn(wst, x)

def eval_infix(wst, x):
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
    cmd, args, children = split_expr(x)
    assert children == []
    ix = [cmd, *args]

    if len(ix) == 1:
        return ix[0]
    assert len(ix) > 2

    first_arg, first_op, second_arg, *rest = x
    xx = [first_op, first_arg, second_arg]

    for i in range(3, len(ix)):
        t = ix[i]
        if i % 2:
            assert first_op == t
        else:
            xx = [first_op, xx, t]
    return xx

def read_indent():
    r = Reader(filename = sys.argv[1])
    #print(list(r.read_tokens()))

    t = r.next_token()
    if t == None:
        return

    assert t != '\n'
    assert t[0] != ' '

    yield '('
    yield t
    depth = 0
    while t := r.next_token():
        if t[0] == ' ':
            continue

        if t != '\n':
            yield t
            continue

        yield t

        nt = r.peek_token()
        if nt == None:
            break

        if nt[0] == ' ':
            t = r.next_token()
            new_depth = calc_depth(t)
        else:
            new_depth = 0

        delta = new_depth - depth

        if delta > 1:
            assert False
        if delta == 1:
            yield '('
        elif delta  == 0:
            yield ')'
            yield '('
        elif delta < 0:
            for i in range(0, delta, -1):
                yield ')'
        depth = new_depth

    for i in range(depth+1):
        yield ')'

def parse_tree(tokens):
    x = []
    stack = [x]
    for t in tokens:
        if t == '(':
            x = []
            stack.append(x)
        elif t == ')':
            stack.pop()
            tos = stack[-1]
            tos.append(x)
            x = tos
        elif t[-1] == '(':
            cmd = t[:-1]
            x = [cmd]
            stack.append(x)
        else:
            x.append(t)

    assert len(stack) == 1
    ast = stack[-1]
    return ast

def main():
    wst = []
    tokens = list(read_indent())
    for x in parse_tree(tokens):
        eval(wst, x)
    #print(tokens)


if __name__ == '__main__':
    main()

