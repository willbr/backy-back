import fileinput

from sys import argv
from dataclasses import dataclass
from pprint import pprint

states = []
cmds = []

macro_words = {
        ':': ';',
        'fn': 'end-fn',
        }

next_token = None

line_buffer = ""
line_buffer_len = 0
line_offset = 0

input = None

break_chars = " (){}[],\n"
prefix_chars = "({["
evil_chars = '\r\t'
indent_width = 2
indent = 0
new_indent = 0


def get_word():
    state_fn = states[-1]
    # print(f"state={state_fn.__name__}")
    return state_fn()


def push_state(fn, cmd=None):
    states.append(fn)
    cmds.append(cmd)


def pop_state():
    states.pop()
    return cmds.pop()


def main():
    global input

    input = fileinput.input(argv[1])
    get_line()

    push_state(get_indent_head)

    word = get_word()
    while word:
        print(f"{word=}")
        word = get_word()


def get_indent_head():
    nt = peek_token()
    if nt is None:
        return None

    macro_end = macro_words.get(nt)

    if macro_end:
        t = get_token()
        cmds[-1] = macro_end
        push_state(get_indent_body)
        return t
    elif nt in prefix_chars:
        push_state(get_indent_body)
        return get_syntax()
    else:
        t = get_token()
        cmds[-1] = t
        push_state(get_indent_body)
        return get_word()


def get_indent_body():
    global indent

    nt = peek_token()
    if nt is None:
        print("ere")
        return None

    if nt == '\n':
        # print("newline")
        get_token()
        while peek_token() == '\n':
            print("skipping new lines")
            get_token()

        parse_indent()
        # print(f"{new_indent=} {indent=}")
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
    elif nt in prefix_chars:
        return get_syntax()
    elif nt in break_chars:
        print(f"{nt=}")
        debug_state()
        assert False

    t = get_token()

    return t


def get_infix_first_arg():
    nt = peek_token()

    if nt == '\n':
        assert False
    elif nt == ')':
        assert False
    elif nt in prefix_chars:
        pop_state()
        push_state(get_infix_first_op)
        return get_syntax()
    elif nt in break_chars:
        assert False

    t = get_token()
    pop_state()
    push_state(get_infix_first_op)
    return t


def get_infix_first_op():
    nt = peek_token()

    if nt == '\n':
        assert False
    elif nt == ')':
        get_token()
        pop_state()
        return get_word()
    elif nt in prefix_chars:
        debug_state()
        assert False
        return get_syntax()
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
        debug_state()
        assert False
    elif nt == ',':
        get_token()
        pop_state()
        op = pop_state()
        push_state(get_infix_first_arg)
        return op
    elif nt in prefix_chars:
        pop_state()
        push_state(get_infix_next_op)
        return get_syntax()
    elif nt in break_chars:
        debug_state()
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
    elif nt == ',':
        get_token()
        pop_state()
        op = pop_state()
        push_state(get_infix_first_arg)
        return op
    elif nt in prefix_chars:
        assert False
    elif nt in break_chars:
        print(f"{nt=}")
        assert False

    pop_state()

    prev_op = cmds[-1]

    if prev_op != nt:
        print(f"{prev_op=} {nt=}")
        debug_state()
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
    elif nt in prefix_chars:
        return get_syntax()
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
        print(f"{line_buffer=}")
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
        new_indent = 0
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

    escaped = False

    c = line_buffer[end_pos:end_pos+1]
    l = [c]
    end_pos += 1
    c = line_buffer[end_pos:end_pos+1]

    while c != '':
        if c == '"':
            l.append(c)
            end_pos += 1
            break
        elif c == '\\':
            end_pos += 1
            c = line_buffer[end_pos:end_pos+1]
            if c == 'n':
                l.append('\n')
            else:
                raise SyntaxError("Unknown escape code")
                assert False
        else:
            l.append(c)

        end_pos += 1
        c = line_buffer[end_pos:end_pos+1]

    token = ''.join(l)
    line_offset = end_pos

    chomp(' ')
    return token


def get_prefix_head():
    nt = peek_token()
    if nt is None:
        return None

    macro_end = macro_words.get(nt)

    if macro_end:
        t = get_token()
        cmds[-1] = macro_end
        push_state(get_prefix_body)
        return t
    elif nt in prefix_chars:
        return get_syntax()
    else:
        t = get_token()
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
    elif nt in prefix_chars:
        return get_syntax()
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


def get_syntax():
    t = get_token()
    # print(f"{t=}")

    if t == '(':
        push_state(get_infix_first_arg)
        return get_word()
    elif t == '{':
        push_state(get_postfix)
        return get_word()
    elif t == '[':
        push_state(get_prefix_head)
        return get_word()
    else:
        print(f"{t=}")
        debug_state()
        assert False


def debug_state():
    print()

    nt = peek_token()
    print(f"{nt=}")
    print(line_buffer)
    print(line_offset * " ", end="")
    print("^")

    for i in reversed(range(0, len(states), 1)):
        state = states[i].__name__
        print(f"{i} {state} {cmds[i]}")
    print()

if __name__ == "__main__":
    main()

