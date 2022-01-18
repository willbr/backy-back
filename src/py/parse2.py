import sys
import fileinput

new_indent = 0
cur_indent = -1
indent_width = 4
next_token = None
syntax_stack = []


def read_token():
    global next_token
    if next_token:
        token = next_token
        next_token = None
        return token

    return next(file).strip('\n')


def peek_token():
    global next_token
    if next_token:
        return next_token
    next_token = next(file).strip('\n')
    return next_token


def push_token(t):
    global next_token
    if next_token:
        assert False
    next_token = t


def main():
    global file, new_indent, cur_indent
    arg = sys.argv[1]
    file = fileinput.input(arg)

    try:
        token = read_token()
        print('[')
        print(token)
        cur_indent = 0
        while True:
            token = read_token()
            if token == 'ie/newline':
                if syntax_stack:
                    print(syntax_stack)
                    assert False # unmatch syntax
                print(token)
                token = peek_token()
                while token == 'ie/newline':
                    _ = read_token()
                    token = peek_token()

                if token[0] == ' ':
                    space_token = read_token()
                    spaces = len(space_token)
                    assert not spaces % indent_width
                    if peek_token() == 'ie/newline':
                        pass
                    else:
                        new_indent = spaces // indent_width
                else:
                    new_indent = 0

                diff = new_indent - cur_indent

                if peek_token() == '\\':
                    if new_indent == cur_indent + 1:
                        _ = read_token()
                        push_token('ie/backslash')
                    else:
                        assert False
                elif diff > 1:
                    assert False
                elif diff == 1:
                    cur_indent += 1
                    print('[')
                elif diff == 0:
                    print(']')
                    print('[')
                else:
                    for i in range(abs(diff)):
                        cur_indent -= 1
                        print(']')
                    print(']')
                    print('[')
            elif token in '({[':
                print(token)
                syntax_stack.append(token)
            elif token == "ie/neoteric":
                print('[')
                syntax_stack.append('[')
                print(token)
                token = read_token()
                print(token)
                open_char = read_token()
                print(open_char)
                assert open_char in '({['
                syntax_stack.append(open_char)
                syntax_stack.append("neoteric")

            elif token in ')}]':
                open_char = syntax_stack.pop()
                is_neoteric = False
                if open_char == 'neoteric':
                    is_neoteric = True
                    open_char = syntax_stack.pop()

                if open_char == '(':
                    assert token == ')'
                    print(token)
                elif open_char == '{':
                    assert token == '}'
                    print(token)
                elif open_char == '[':
                    assert token == ']'
                    print(token)
                else:
                    print(token)
                    assert False

                if is_neoteric:
                    push_token(']')
            else:
                print(token)

    except StopIteration:
        pass

    for i in range(cur_indent + 1):
        print(']')


if __name__ == '__main__':
    main()

