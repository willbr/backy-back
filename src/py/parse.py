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


def print_expr(x, depth=0, print_brackets=True):

    if is_atom(x):
        print(x, end="")
        return

    if print_brackets:
        print("[", end="")

    if x == []:
        if print_brackets:
            print("]", end="")
        return

    car, *cdr = x

    if not is_atom(car):
        if not print_brackets:
            print("\\\\", end="")
        print("\n" + (depth+1) * "    ", end="")

    print_expr(car, depth+1, print_brackets)

    prev_it = car

    for it in cdr:
        if is_atom(it):
            if is_atom(prev_it):
                print(" ", end="")
            else:
                print("\n" + (depth+1) * "    ", end="")
                if not print_brackets:
                    print("\\ ", end= "")
        else:
            print("\n" + (depth+1) * "    ", end="")

        print_expr(it, depth+1, print_brackets)

        prev_it = it

    if print_brackets:
        print("]", end="")


def puts_expr(x, print_brackets=True):
    print_expr(x, 0, print_brackets)
    print("")


def remove_newline(prog):
    if is_atom(prog):
        return prog

    return [remove_newline(x) for x in prog if x != 'newline']


if __name__ == '__main__':
    prog = parse_file('-')
    for s in remove_newline(prog):
        puts_expr(s, False)
    print()


