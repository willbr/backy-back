import fileinput

from sys import argv
from dataclasses import dataclass
from pprint import pprint

states = []
cmds = []

macro_words = {
        ':': ';',
        }

next_token = None

line_buffer = ""
line_buffer_len = 0
line_offset = 0

input = None

break_chars = " (){}[],\n"
evil_chars = ' \r\t'
indent_width = 2
indent = 0
new_indent = 0


def get_word():
    state_fn = states[-1]
    return state_fn()


def push_state(fn, cmd=None):
    states.append(fn)
    cmds.append(cmd)


def pop_state():
    states.pop()
    return cmds.pop()


def main():
    global input
    global get_word

    input = fileinput.input(argv[1])
    get_line()

    push_state(get_indent_head)

    word = get_word()
    while word:
        # print(f"{word=} {indent=} {new_indent=}")
        print(f"{word=}")
        word = get_word()


def get_indent_head():
    t = get_token()
    if t is None:
        return None

    macro_end = macro_words.get(t)

    if macro_end:
        cmds[-1] = macro_end
        push_state(get_indent_body)
        return t
    elif t == '(':
        assert False
    elif t == '{':
        assert False
    elif t == '[':
        push_state(get_prefix_head)
        return get_word()
    else:
        cmds[-1] = t
        push_state(get_indent_body)
        return get_word()


def get_indent_body():
    global indent

    nt = peek_token()
    if nt is None:
        return None

    if nt == '\n':
        get_token()
        while peek_token() == '\n':
            print("skipping new lines")
            get_token()

        parse_indent()
        if new_indent == indent + 1:
            nt = peek_token()
            if nt == None:
                debug_state()
                raise SyntaxError("EOF after indent")
                pass
            elif nt == '\\':
                get_token()
                t = get_token()
                return t
            indent = new_indent
            push_state(get_indent_head)
            return get_word()
        elif new_indent > indent:
            raise SyntaxError("invalid indent")
        elif new_indent == indent:
            pass
        else:
            pop_state()
            t = pop_state()
            push_state(get_dedent)
            return t

        pop_state()
        t = pop_state()
        push_state(get_indent_head)
        return t
    elif nt == '\\':
        get_token()
        t = get_token()
        return t
    elif nt == '(':
        get_token()
        push_state(get_infix_first_arg)
        return get_word()
    elif nt == '[':
        get_token()
        push_state(get_prefix_head)
        return get_word()
    elif nt == '{':
        get_token()
        push_state(get_postfix)
        return get_word()
    elif nt in break_chars:
        print(f"{nt=}")
        debug_state()
        assert False

    t = get_token()

    return t


def get_infix_first_arg():
    nt = peek_token()
    # print(f"{nt=}")

    if nt == '\n':
        assert False
    elif nt == ')':
        assert False
    elif nt in break_chars:
        assert False

    t = get_token()
    pop_state()
    push_state(get_infix_first_op)
    return t


def get_infix_first_op():
    nt = peek_token()
    # print(f"{nt=}")

    if nt == '\n':
        assert False
    elif nt == ')':
        assert False
    elif nt in break_chars:
        assert False

    t = get_token()
    cmds[-1] = t

    push_state(get_infix_next_arg)
    return get_word()


def get_infix_next_arg():
    nt = peek_token()
    # print(f"{nt=}")

    if nt == '\n':
        assert False
    elif nt == ')':
        assert False
    elif nt in break_chars:
        assert False

    t = get_token()
    pop_state()
    push_state(get_infix_next_op)
    return t


def get_infix_next_op():
    nt = peek_token()
    # print(f"{nt=}")

    if nt == '\n':
        assert False
    elif nt == ')':
        get_token()
        pop_state()
        op = pop_state()
        return op
    elif nt in break_chars:
        assert False

    pop_state()

    prev_op = cmds[-1]

    if prev_op != nt:
        assert False

    t = get_token()
    push_state(get_infix_next_arg)
    return t


def get_postfix():
    nt = peek_token()
    # print(f"{nt=}")

    if nt == '\n':
        assert False
    elif nt == '}':
        get_token()
        pop_state()
        return get_word()
    elif nt in break_chars:
        assert False

    return get_token()


def get_dedent():
    global indent

    if new_indent == indent:
        push_state(get_indent_head)
        return get_word()

    indent -= 1
    pop_state()
    pop_state()
    cmd = pop_state()
    push_state(get_dedent)
    return cmd


def get_line():
    global line_buffer
    global line_buffer_len
    global line_offset
    line_buffer = input.readline()
    line_buffer_len = len(line_buffer)
    line_offset = 0


def chomp(c):
    global line_offset
    nc = line_buffer[line_offset:line_offset+1]
    while nc == c and nc != '':
        line_offset += 1
        nc = line_buffer[line_offset]


def peek_token():
    global next_token
    if next_token == None:
        next_token = get_token()

    return next_token


def get_token():
    global line_offset
    global next_token

    if next_token:
        t, next_token = next_token, None
        return t

    if line_offset >= line_buffer_len:
        get_line()
        while line_buffer == '\n':
            get_line()
        if line_buffer == '':
            return None

    c = line_buffer[line_offset:line_offset+1]

    if c in evil_chars:
        print(f"{c=}")
        assert False

    start_pos = end_pos = line_offset

    if c == ' ':
        chomp(' ')
        token = line_buffer[start_pos:line_offset]
        return token


    if c == '"':
        return get_string()

    if c in break_chars:
        line_offset += 1
        chomp(' ')
        return c

    for c in line_buffer[line_offset:]:
        if c in break_chars:
            break
        end_pos += 1

    token = line_buffer[start_pos:end_pos]
    line_offset = end_pos

    chomp(' ')

    return token


def parse_indent():
    global new_indent

    s = peek_token()
    if s is None:
        new_indent = indent
        return

    # print(f"{s=}")
    if s[0] == ' ':
        s = get_token()
        new_indent = len(s) // indent_width
        if len(s) % indent_width != 0:
            print(f"{len(s) % indent_width}")
            raise SyntaxError
    else:
        new_indent = 0
        
        
def get_string():
    global line_offset

    start_pos = end_pos = line_offset
    end_pos += 1

    for c in line_buffer[end_pos:]:
        if c == '"':
            end_pos += 1
            break
        elif c == '\\':
            assert False

        end_pos += 1

    token = line_buffer[start_pos:end_pos]
    line_offset = end_pos

    chomp(' ')
    return token


def get_prefix_head():
    t = get_token()
    if t is None:
        return None

    macro_end = macro_words.get(t)

    if macro_end:
        cmds[-1] = macro_end
        push_state(get_prefix_body)
        return t
    else:
        cmds[-1] = t
        push_state(get_prefix_body)
        return get_word()


def get_prefix_body():
    nt = peek_token()
    if nt is None:
        return None

    if nt == '\n':
        assert False
        get_token()
        while peek_token() == '\n':
            print("skipping new lines")
            get_token()

    if nt == '\\':
        raise SyntaxError
    elif nt == '(':
        get_token()
        push_state(get_infix_first_arg)
        return get_word()
    elif nt == '[':
        get_token()
        push_state(get_prefix_head)
        return get_word()
    elif nt == '{':
        get_token()
        push_state(get_postfix)
        return get_word()
    elif nt == ']':
        get_token()
        pop_state()
        cmd = pop_state()
        return cmd
    elif nt in break_chars:
        print(f"{nt=}")
        debug_state()
        assert False

    t = get_token()

    return t


def debug_state():
    for i in range(len(states)-1,0,-1):
        print(i, states[i], cmds[i])

if __name__ == "__main__":
    main()

