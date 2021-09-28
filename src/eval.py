import fileinput
import argparse

parser = argparse.ArgumentParser(description='Eval thingy')
parser.add_argument('--trace', action='store_true')
args = parser.parse_args()

stack = []
env = None
input = fileinput.input("-")

def main():
    init()

    token = input.readline().strip()
    while token != '':
        eval(token)
        token = input.readline().strip()


def init():
    global env
    env = {
            '+': [fn_add],
            '*': [fn_mult],
            '.': [fn_dot],
            ':': [fn_defn],
            }


def eval(token):
    if args.trace:
        print(f"{stack=}")
        print(f"{token=}")

    try:
        i = int(token)
        stack.append(i)
        return
    except ValueError:
        pass

    specs = env.get(token, None)
    # print("body", body)
    # print("token", token)

    if specs == None:
        print("token", token)
        raise ValueError(token)

    spec = specs[0]
    spec_type = type(spec)
    if spec_type is list:
        for op in spec:
            eval(op)
    elif callable(spec_type):
        spec()
    else:
        raise ValueError("unknown function type")


def fn_defn():
    name = input.readline().strip()
    body = []

    token = input.readline().strip()
    while token != ";" and token != '':
        body.append(token)
        token = input.readline().strip()

    if name in env.keys():
        env[name].append(body)
    else:
        env[name] = [body]


def fn_add():
    n2 = stack.pop()
    n1 = stack.pop()
    stack.append(n1 + n2)


def fn_mult():
    n2 = stack.pop()
    n1 = stack.pop()
    stack.append(n1 * n2)


def fn_dot():
    print(stack.pop())


if __name__ == '__main__':
    main()

