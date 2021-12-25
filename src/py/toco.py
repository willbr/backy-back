from parse import parse_file, is_atom, remove_newline

libs = set()
functions = {}
infix_symbols = "= == != *".split()


def compile(x):
    head, *args = x
    if head == 'fn':
        compile_fn(*args)
    elif head == 'include-lib':
        compile_lib(*args)
    else:
        print(head)
        assert False


def compile_lib(lib_name, *body):
    assert body == ('newline',)
    libs.add(lib_name)


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

    if args[0] == "=":
        args = [head, ['infix', *args[1:]]]
        head = '='

    if args[0] in infix_symbols:
        head, *args = transform_infix([head] + args)

    if head == 'while':
        return compile_while(args, body)
    elif head == 'var':
        return compile_var(args, body) + ";"

    assert body == []
    ce = compile_expression([head, *args])
    if ce[0] == "(" and ce[-1] == ")":
        ce = ce[1:-1]
    return ce + ";"


def compile_var(args, body):
    assert body == []
    var_name, var_type, var_val = args
    return f"{var_type} {var_name} = {var_val}"


def compile_while(pred, body):
    cpred = compile_expression(transform_infix(pred))
    cbody = [compile_statement(s) for s in body]
    return f"while ({cpred})", cbody


def compile_expression(x):
    if is_atom(x):
        if x[0] == '"':
            return x
        return x

    head, *rest = x

    if head == 'infix':
        if x == ['infix']:
            return ''
        head, *rest = transform_infix(rest)

    args, body = split_newline(rest)
    assert body == None
    cargs = [compile_expression(a) for a in args]

    if head in infix_symbols:
        # print(head, cargs)
        return "(" + f" {head} ".join(cargs) + ")"
    else:
        return f"{head}({', '.join(cargs)})"


def transform_infix(x):
    n = len(x)
    # print(x)
    # print(n)
    # print(n % 2)

    if n == 0:
        return x
    elif n == 1:
        assert False
    elif (n % 2) == 0:
        print(x)
        assert False

    first_arg, first_op, *rest = x
    xx = [first_op, first_arg]
    for i in range(2, len(x)):
        if i % 2:
            assert first_op == x[i]
        else:
            xx.append(x[i])
    return xx


def split_newline(x):
    try:
        pos = x.index('newline')
        lhs = x[:pos]
        rhs = x[pos+1:]
    except ValueError:
        lhs = x
        rhs = None
    finally:
        return lhs, rhs


def print_block(body, depth):
    print("{")
    indent = "    " * depth

    for s in body:
        print(indent, end="")
        if isinstance(s, str):
            print(s)
        else:
            head, sub = s
            print(head + " ", end="")
            print_block(sub, depth+1)

    indent = "    " * (depth-1)
    print(indent + "}")


if __name__ == "__main__":
    prog = parse_file("-")

    for x in prog:
        compile(x)

    for name in libs:
        name = name.strip('"')
        print(f"#include <{name}>")

    if libs:
        print()

    for name, spec in functions.items():
        print("void")
        print(f"{name}(void) ", end="")
        print_block(spec, 1)
    print()


