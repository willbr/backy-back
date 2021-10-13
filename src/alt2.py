import fileinput

from pprint import pprint
from enum import IntEnum, auto

class State(IntEnum):
    indent_expr_head = auto()
    indent_expr_body = auto()
    prefix_expr_head = auto()
    prefix_expr_body = auto()
    infix_first_arg  = auto()
    infix_first_op   = auto()
    infix_other_arg  = auto()
    infix_other_op   = auto()

state_stack = [[State.indent_expr_head, None]]
input_queue = []
line_buffer = ""
line_buffer_len = 0
line_offset = 0
input = None
break_chars = " (){}[],\n"
evil_chars = ' \r\t'
indent_width = 2
indent = 0

def main():
    global input

    input = fileinput.input("-")
    get_line()

    token = next_token()
    while token:
        print(f"{token=}")
        token = next_token()


def next_token():
    global indent

    if not input:
        return None

    if input_queue:
        t = input_queue.pop(0)
    else:
        t = parse_token()

    if True:
        print('')
        print(f"{t=}")
        print("state_stack=")
        print('\n'.join(map(str, state_stack)))

    if t is None:
        return None

    top = state_stack[-1]
    state, cmd = top

    if t == '(':
        state_stack.append([State.infix_first_arg, None])
        return next_token()
    elif t == '(':
        assert False
    elif t == '[':
        assert False
    elif t == ']':
        assert False
    elif t == '\\':
        assert False
    elif state == State.indent_expr_head:
        top[1] = t
        state_stack.append([State.indent_expr_body, None])
        return next_token()
    elif state == State.indent_expr_body:
        if t == '\n':
            return pop_state()
        else:
            return t
    elif state == State.infix_first_arg:
        state_stack.pop()
        nt = next_token()
        state_stack.append([State.infix_first_op, nt])
        return next_token()
    elif state == State.infix_first_op:
        print(f"{t=}")
        assert False
    else:
        print(f"{state_stack[-1]=}")
        assert False


def get_line():
    global line_buffer
    global line_buffer_len
    global line_offset
    line_buffer = input.readline()
    line_buffer_len = len(line_buffer)
    line_offset = 0


def parse_newline():
    global line_offset
    global indent

    print("\tparse_newline")
    get_line()

    print(f"{line_buffer=}")

    if line_buffer == '':
        print("empty line_buffer")
        return None

    start_pos = end_pos = line_offset
    c = line_buffer[line_offset]
    while c == ' ' and c != '':
        line_offset += 1
        c = line_buffer[line_offset]
    end_pos = line_offset

    if c == '':
        assert False

    top = state_stack[-1]
    state, cmd = top

    print(f"{state=}")

    delta = end_pos - start_pos
    new_indent = delta // indent_width
    indent_delta = new_indent - indent

    if indent_delta == 1:
        assert False
    elif indent_delta > 1:
        raise SyntaxError("bad indentation")
    elif indent_delta == 0:
        assert False
    else:
        assert False

    assert False


def chomp(c):
    global line_offset
    nc = line_buffer[line_offset:line_offset+1]
    while nc == c and nc != '':
        line_offset += 1
        nc = line_buffer[line_offset]

def parse_token():
    global line_offset
    if line_offset >= line_buffer_len:
        t = parse_newline()
        if t:
            return t

    chomp(' ')

    c = line_buffer[line_offset:line_offset+1]

    if c == '':
        assert False

    if c in evil_chars:
        print(f"{c=}")
        assert False

    if c in break_chars:
        line_offset += 1
        return c

    start_pos = end_pos = line_offset
    for c in line_buffer[line_offset:]:
        if c in break_chars:
            break
        end_pos += 1

    token = line_buffer[start_pos:end_pos]
    line_offset = end_pos

    return token


def pop_state():
    top = state_stack[-1]
    state, cmd = top
    if state == State.indent_expr_body:
        state_stack.pop()
        top = state_stack[-1]
        state, cmd = top
        top[1] = None
        return cmd
    else:
        assert False


if __name__ == "__main__":
    main()

