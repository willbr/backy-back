import sys
import fileinput

new_indent = 0
cur_indent = -1
indent_width = 4
next_token = None

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
            if token == 'newline':
                print(token)
                token = peek_token()
                if token[0] == ' ':
                    _ = read_token()
                    spaces = len(token)
                    assert not spaces % indent_width
                    new_indent = spaces // indent_width
                else:
                    new_indent = 0

                diff = new_indent - cur_indent

                if peek_token() == '\\':
                    if new_indent == cur_indent + 1:
                        _ = read_token()
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
            else:
                print(token)
    except StopIteration:
        pass

    for i in range(cur_indent + 1):
        print(']')


if __name__ == '__main__':
    main()

