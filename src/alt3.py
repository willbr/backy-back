import fileinput

from dataclasses import dataclass
from pprint import pprint

cmds = []
state = "indent head"
next_token = None

line_buffer = ""
line_buffer_len = 0
line_offset = 0

input = None

break_chars = " (){}[],\n"
evil_chars = '\r\t'
indent_width = 2
indent = 0
new_indent = 0


def main():
    global input

    input = fileinput.input("-")
    get_line()

    word = get_word()
    while word:
        print(f"{word=}")
        word = get_word()


def get_word():
    global state
    global indent
    global cmds

    # print(f"{states=}")
    # print(f"{new_indent=} {indent=}")
    if new_indent == indent + 1:
        indent = new_indent
    elif new_indent == indent:
        # print(f"{states=}")
        pass
    elif new_indent < indent:
        indent -= 1
        cmd = cmds.pop()
        return cmd
    elif new_indent > indent:
        raise SyntaxError

    # print(f"{t=}")


    t = get_token()
    if t is None:
        return None


    if state == "indent head":
        cmds.append(t)
        state = "indent tail"
        return get_word()
    elif state == "indent tail":
        if t == '\n':
            parse_indent()
            if new_indent == indent + 1:
                nt = peek_token()
                if nt == '\\':
                    _ = get_token()
                    return get_token()
                else:
                    state = "indent head"
                    return get_word()
            elif new_indent == indent:
                cmd = cmds.pop()
                return cmd
            elif new_indent < indent:
                cmd = cmds.pop()
                state = "indent head"
                return cmd
            else:
                return get_word()
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


    start_pos = end_pos = line_offset

    if c == ' ':
        chomp(' ')
        token = line_buffer[start_pos:line_offset]
        return token

    if c in break_chars:
        # print("break char")
        line_offset += 1
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


if __name__ == "__main__":
    main()

