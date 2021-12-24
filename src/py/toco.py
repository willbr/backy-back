from parse import parse_file, is_atom, remove_newline

functions = {}

def compile(x):
    head, *args = x
    if head == 'fn':
        compile_fn(*args)
    else:
        assert False


def compile_fn(fn_name, *spec):
    assert spec[0] == 'newline'
    body = []
    for x in spec[1:]:
        s = compile_statement(x)
        body.append(s)

    functions[fn_name] = body


def compile_statement(x):
    head, *rest = x
    args, body = split_newline(rest)
    # print(x)
    # print(head)
    # print(args)
    # print(body)
    cargs = ', '.join(compile_expression(a) for a in args)
    assert body == []
    return f"{head}({cargs});"


def compile_expression(x):
    if is_atom(x):
        if x[0] == '"':
            return x
        assert False

    print(x)
    assert False


def split_newline(x):
    pos = x.index('newline')
    lhs = x[:pos]
    rhs = x[pos+1:]
    return lhs, rhs


if __name__ == "__main__":
    prog = parse_file("-")

    for x in prog:
        compile(x)

    for name, spec in functions.items():
        print("void")
        print(f"{name}(void) {{")
        for s in spec:
            print("    " + s)
        print("}")


