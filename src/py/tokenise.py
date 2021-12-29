import fileinput
import sys

file = None
i = 0
line = ""
len_line = 0
next_token = None
breakchars = " \t\n()[]{}"


def get_line():
    global i, line, len_line
    line = next(file)
    len_line = len(line)
    i = 0


def chomp(chars):
    global i
    while i < len_line and line[i] in chars:
        i += 1


def read_string():
    global i
    start_pos = i
    assert line[i] == '"'
    i += 1

    while i < len_line and line[i] not in '"':
        i += 1

    assert line[i] == '"'

    i += 1
    word = line[start_pos:i]
    return word


def read_token():
    global i
    start_pos = i
    while i < len_line and line[i] not in breakchars:
        i += 1

    if line[i] in '({[':
        i += 1

    len_word = i - start_pos
    assert len_word
    word = line[start_pos:i]
    return word


def next_word():
    global i, next_token

    if next_token:
        word = next_token
        next_token = None
        return word

    if i >= len_line:
        get_line()

    if line[i] == '\n':
        get_line()
        chomp(' ')
        next_token = ' ' * i
        word = 'newline'

    elif line[i] == '"':
        word = read_string()

    elif line[i] == '\t':
        assert False

    elif line[i] in breakchars:
        word = line[i]
        i += 1

    else:
        word = read_token()

    chomp(' ')
    return word


def main():
    global file
    arg = sys.argv[1]
    file = fileinput.input(arg)
    try:
        while True:
            w = next_word()
            print(w)
    except StopIteration:
        pass


if __name__ == "__main__":
    main()

