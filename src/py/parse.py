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


def is_atom(x):
    return not isinstance(x, list)


def print_expr(x, depth=0, wrap=False):

    if is_atom(x):
        print(x, end="")
        return

    print("[", end="")

    car, *cdr = x

    print_expr(car, depth+1)

    prev_it = car

    for it in cdr:
        if is_atom(it):
            if is_atom(prev_it):
                print(" ", end="")
            else:
                print("\n" + (depth+1) * "    ", end="")
            print_expr(it, depth+1)
        else:
            print("\n" + (depth+1) * "    ", end="")
            print_expr(it, depth+1)
        prev_it = it

    print("]", end="")


if __name__ == '__main__':
    prog = parse_file('-')
    # pprint(prog)
    print()
    for x in prog:
        # print('x:', x)
        print_expr(x)
        print("\n")
    print()

