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


if __name__ == '__main__':
    prog = parse_file('-')
    pprint(prog)

