import fileinput

from dataclasses import dataclass
from pprint import pprint

@dataclass
class State:
    name: str
    cmd: any


states = []
top_state = None
next_token = None

line_buffer = ""
line_buffer_len = 0
line_offset = 0

input = None

break_chars = " (){}[],\n"
evil_chars = ' \r\t'
# indent_width = 2
# indent = 0


def main():
    global input

    input = fileinput.input("-")
    get_line()

    word = get_word()
    while word:
        print(f"{word=}")
        word = get_word()


def get_word():
    global top_state

    t = get_token()

    if t is None:
        return None

    if top_state == None:
        top_state = State('indent expr', t)
        states.append(top_state)
        return get_word()

    if top_state.name == "indent expr":
        if t == '\n':
            nt = peek_token()
            if nt is None:
                cmd = pop_state()
                return cmd
            assert False
        return t
    else:
        assert False

    return t


def get_line():
    global line_buffer
    global line_buffer_len
    global line_offset
    # print("get_line")
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

    # print(f"{line_buffer=}")
    # print(f"{line_offset=} {line_buffer_len=}")

    if line_offset >= line_buffer_len:
        get_line()
        while line_buffer == '\n':
            get_line()
        if line_buffer == '':
            return None

    c = line_buffer[line_offset:line_offset+1]
    # print(f"{c=}")

    if c in evil_chars:
        print(f"{c=}")
        assert False

    if c in break_chars:
        # print("break char")
        line_offset += 1
        return c

    start_pos = end_pos = line_offset
    for c in line_buffer[line_offset:]:
        if c in break_chars:
            break
        end_pos += 1

    token = line_buffer[start_pos:end_pos]
    line_offset = end_pos

    chomp(' ')

    return token


def pop_state():
    global top_state
    cmd = top_state.cmd
    top_state = states.pop()
    return cmd


if __name__ == "__main__":
    main()

