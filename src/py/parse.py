from pprint import pprint
import fileinput


def parse_file(filename):
    stack = [[]]

    for line in fileinput.input(filename):
        token = line.strip()

        if token == '[':
            stack.append([])
        elif token == '(':
            stack.append(["infix"])
        elif token == '{':
            stack.append(["postfix"])
        elif token in (']', ')', '}'):
            tos = stack.pop()
            stack[-1].append(tos)
        else:
            stack[-1].append(token)

    prog = stack[0]
    return prog


def isatom(x):
    return not isinstance(x, list)

def print_expr(x, depth=0, wrap=False):
    if isatom(x):
        print(x, end="")
        return

    # print()
    print(depth * "    ", end="")

    for e in x:
        if e == 'newline':
            print()
        elif isatom(e):
            print_expr(e)
            print(" ", end="")
        else:
            print_expr(e, depth+1)


if __name__ == '__main__':
    prog = parse_file('-')
    # pprint(prog)
    print()
    for x in prog:
        print_expr(x)
    print()

