import fileinput
import argparse
from pprint import pprint

parser = argparse.ArgumentParser(description='Eval thingy')
parser.add_argument('--trace', action='store_true')
args = parser.parse_args()


input_stack = []
param_stack = []
env = None
input = fileinput.input("-")
imediate_cmds = [':', 'do']


def main():
    init()

    token = next_token()
    while token != '':
        eval(token)
        token = next_token()
    print(f"\n\n{param_stack=}")


def init():
    global env
    env = {
            '+':    [fn_add],
            '-':    [fn_sub],
            '*':    [fn_mult],
            '.':    [fn_dot],
            '.s':   [fn_print_stack],
            ':':    [fn_defn],
            '[':    [fn_prefix_expr],
            '{':    [fn_postfix_expr],
            '(':    [fn_infix_expr],
            'emit': [fn_emit],
            'do':   [fn_do],
            }


def eval(token):
    if args.trace:
        print(f"{input_stack=}")
        print(f"{param_stack=}")
        print(f"{token=}")
        print("")

    if token[0] == '"':
        param_stack.append(token)
        return

    try:
        i = int(token)
        param_stack.append(i)
        return
    except ValueError:
        pass

    specs = env.get(token, None)

    if specs == None:
        # pprint(env)
        print(f"{token=}")
        raise ValueError(token)

    spec = specs[0]
    spec_type = type(spec)

    if spec_type is list:
        input_stack.extend(reversed(spec))
    elif callable(spec_type):
        spec()
    else:
        raise ValueError("unknown function type")


def fn_defn():
    name = next_token()
    body = []

    token = next_token()
    while token != ";" and token != '':
        body.append(token)
        token = next_token()

    if name in env.keys():
        env[name].append(body)
    else:
        env[name] = [body]


def parse_prefix():
    cmd = next_token()
    expr = []

    token = next_token()
    while token != "]" and token != '':
        if token == '[':
            child = parse_prefix()
            if child:
                expr.extend(child)
        elif token == '(':
            child = parse_infix()
            if child:
                expr.extend(child)
        else:
            expr.append(token)

        token = next_token()

    expr.append(cmd)

    # print(f"{expr=}")
    return expr


def fn_prefix_expr():
    *body, cmd = parse_prefix()

    its_an_imediate_cmd = cmd in imediate_cmds
    it_isnt_an_imediate_cmd = not its_an_imediate_cmd

    if its_an_imediate_cmd:
        if cmd == ':':
            body.insert(0, ':')
            body.append(';')
        elif cmd == 'do':
            body.insert(3, 'do')
            body.append('loop')
        else:
            raise ValueError(f"unknown {cmd=}")
    else:
        body.append(cmd)

    # print(f"{body=}")

    input_stack.extend(reversed(body))


def parse_postfix():
    expr = []
    token = next_token()
    while token != "}" and token != '':
        # print(f"{token=} {expr=}")
        if token == '[':
            assert False
            child = parse_prefix()
            if child:
                expr.extend(child)
        elif token == '{':
            assert False
        else:
            expr.append(token)

        token = next_token()

    return expr


def fn_postfix_expr():
    body = parse_postfix()
    input_stack.extend(reversed(body))


def parse_infix():
    parent_tokens = []
    infix_tokens = []
    token = next_token()

    while token != ")" and token != '':
        # print(f"{token=} {expr=}")
        if token == '[':
            assert False
            child = parse_prefix()
            if child:
                infix_tokens.extend(child)
        elif token == '{':
            assert False
        elif token == '(':
            child = parse_infix()
            if child:
                infix_tokens.extend(child)
        elif token == ',':
            parent_tokens.append(infix_tokens)
            infix_tokens = []
        else:
            infix_tokens.append(token)

        token = next_token()

    parent_tokens.append(infix_tokens)

    expr = []
    for infix_tokens in parent_tokens:
        # print(f"{infix_tokens=}")
        count = len(infix_tokens)

        if count == 0:
            continue
        elif count == 1:
            expr.append(infix_tokens[0])
            continue

        arg, op, next_arg, *tail = infix_tokens
        expr.extend([arg, next_arg, op])
        # print(f"{arg=} {op=} {next_arg=} {tail=}")
        while tail:
            next_op, next_arg, *tail = tail
            if op != next_op:
                raise ValueError(f"operator precidence: {op=} {next_op=}")
            # print(f"{op=} {next_op=} {next_arg=}")
            expr.extend([next_arg, next_op])
            # print(f"{expr=}")

    return expr


def fn_infix_expr():
    body = parse_infix()
    print(f"{body=}")
    input_stack.extend(reversed(body))


def next_token():
    if input_stack:
        return input_stack.pop()
    else:
        return input.readline().strip()


def fn_add():
    n2 = param_stack.pop()
    n1 = param_stack.pop()
    param_stack.append(n1 + n2)


def fn_sub():
    n2 = param_stack.pop()
    n1 = param_stack.pop()
    param_stack.append(n1 - n2)


def fn_mult():
    n2 = param_stack.pop()
    n1 = param_stack.pop()
    param_stack.append(n1 * n2)


def fn_dot():
    print(param_stack.pop())


def fn_emit():
    n1 = param_stack.pop()
    print(chr(n1), end="")


def fn_do():
    body = []
    step  = param_stack.pop()
    start = param_stack.pop()
    limit = param_stack.pop()

    token = next_token()
    while token != "loop" and token != '':
        body.append(token)
        token = next_token()

    for i in range(start, limit, step):
        for token in body:
            eval(token)


def fn_print_stack():
    print(f"{param_stack}")


if __name__ == '__main__':
    main()

