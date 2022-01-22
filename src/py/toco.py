from parse2_syntax import parse_file, is_atom, remove_newline, puts_expr
from pprint import pprint

libs = set()
types = {}
structs = {}
functions = {}
global_vars = {}
top_level = []
infix_symbols = """
= == !=
+ += - -= * *= / /=
> >= < <=
and or
""".split()


def compile(x):
    # pprint(x)
    head, *args = x
    if head == 'fn':
        compile_fn(*args)
    elif head == 'include-lib':
        compile_lib(*args)
    elif head == 'struct':
        compile_struct(*args)
    elif head == 'globals':
        compile_globals(args)
    elif head == 'typedef':
        compile_typedef(*args)
    elif head == 'define':
        compile_define(*args)
    elif head == 'ie/newline':
        assert args == []
    else:
        print(head)
        assert False


def mangle(name):
    return name.replace('-', '_')

def compile_define(define_name, *body):
    decl = f"#define {define_name} {body[0]}"
    top_level.append(decl)


def compile_typedef(type_name, *body):
    # print(type_name)
    type_spec, rest = split_newline(body)
    assert rest == ()
    # print(type_spec)
    decl = "typedef " + compile_var_decl(type_name, type_spec[0]) + ";"
    # print(decl)
    # assert False
    top_level.append(decl)


def compile_struct(struct_name, *body):
    assert body[0] == 'ie/newline'
    assert len(body) > 1
    struct_spec = {}
    for member_spec in body[1:]:
        member_name, member_type, nl = member_spec
        assert nl == 'ie/newline'
        struct_spec[member_name] = member_type
    types[struct_name] = ['struct', struct_spec]
    structs[struct_name] = struct_spec

    struct_decl = [f"struct {struct_name} {{"]
    for member_name, member_type in struct_spec.items():
        decl = compile_var_decl(member_name, member_type)
        struct_decl.append(f"    {decl};")
    struct_decl.append("};")
    top_level.append('\n'.join(struct_decl) + '\n')



def compile_globals(body):
    assert body[0] == 'ie/newline'
    body.pop(0)
    for elem in body:
        assert len(elem) == 4
        var_name, let, x, nl = elem
        var_name = mangle(var_name)
        assert let == ':='
        assert nl == 'ie/newline'
        neoteric, var_type, var_initial = x
        assert neoteric == 'ie/neoteric'
        # print(var_initial)
        # print(x)
        decl = compile_var_decl(var_name, var_type, var_initial)
        # print(decl)
        # print()
        global_vars[var_name] = decl
        top_level.append(decl + ";")


def compile_lib(lib_name, *body):
    assert body == ('ie/newline',)
    libs.add(lib_name)


def compile_fn(fn_name, *spec):
    cbody = []
    params = []

    if not is_atom(fn_name):
        if fn_name[0] == 'ie/neoteric':
            assert len(fn_name) == 3
            raw_params = fn_name[2]
            fn_name    = fn_name[1]
        else:
            assert False

        if raw_params[0] == 'ie/infix':
            raw_params = split_on_commas(raw_params[1:])
            params = compile_params(raw_params)
        else:
            assert False

    returns, body = split_newline(spec)

    n = len(returns)
    if n == 0:
        returns = 'void'
        pass
    elif n == 1:
        returns = returns[0]
    else:
        assert False

    if body[0][0] == 'params':
        assert params == []
        params = compile_params(body[0][1:])
        body = body[1:]

    if spec[0][0] == 'returns':
        assert returns == None
        returns = compile_returns(body[0][1:])
        body = body[1:]
    elif returns == None:
        returns = 'void'

    for x in body:
        # pprint(x)
        s = compile_statement(x)
        cbody.append(s)

    functions[fn_name] = [params, returns, cbody]


def compile_params(spec):
    if spec[0] == 'ie/newline':
        spec = spec[1:]

    params = []
    for param in spec:
        if len(param) == 3:
            assert param.pop() == 'ie/newline'
        var_name, var_type = param
        params.append(compile_var_decl(var_name, var_type))
    return params


def compile_returns(spec):
    assert spec[1] == 'ie/newline'
    assert len(spec) == 2
    return spec[0]


def print_func_decl(name, params, returns, sep='\n'):
    if params:
        cparams = ', '.join(params)
    else:
        cparams = 'void'
    print(f"{returns}{sep}{name}({cparams})", end="")


def compile_var_decl(var_name, var_type, initial_value=None):
    is_struct = var_type == 'struct'

    if is_struct:
        if is_atom(initial_value):
            assert False
        head, *rest = initial_value
        iv = transform_infix(rest)
        struct_name, *struct_values = iv
        var_type += f" {struct_name}"

    lhs = ""
    rhs = ""

    while var_type[0] == '*':
        lhs = "*" + lhs
        var_type = var_type[1:]

    decl = f"{var_type} {lhs}{var_name}{rhs}"

    if is_struct and initial_value:
        decl += " = {" + ', '.join(struct_values) + "}"
    elif initial_value:
        ce = compile_expression(initial_value)
        decl += f" = {ce}"

    return decl


def compile_statement(x):
    head, *rest = x
    args, body = split_newline(rest)

    if args == []:
        pass
    elif args[0] == "=":
        args = [head, ['ie/infix', *args[1:]]]
        head = '='

    if args == []:
        pass
    elif args[0] in infix_symbols:
        nx = transform_infix([head] + args)
        if is_atom(nx):
            return nx
        head, *args = nx

    if head == 'while':
        return compile_while(args, body)
    elif head == 'var':
        return compile_var(args, body) + ";"
    elif head == 'if':
        return compile_if(args, body)

    assert body == [] or body == None
    ce = compile_expression([head, *args])
    return ce + ";"


def compile_var(args, body):
    assert body == []
    num_args = len(args)
    if num_args == 2:
        var_name, var_type = args
        return f"{var_type} {var_name}"
    elif num_args == 3:
        var_name, var_type, var_val = args
        return f"{var_type} {var_name} = {var_val}"
    else:
        assert False


def compile_if(pred, body):
    cpred = compile_expression(transform_infix(pred))
    cbody = [compile_statement(s) for s in body]
    return f"if ({cpred})", cbody


def compile_while(pred, body):
    cpred = compile_expression(transform_infix(pred))
    cbody = [compile_statement(s) for s in body]
    return f"while ({cpred})", cbody


def compile_expression(x, depth=0):
    if is_atom(x):
        return mangle(x)

    # print(x)
    head, *rest = x


    while head in ['ie/infix', 'ie/neoteric']:
        if head == 'ie/infix':
            if x == ['ie/infix']:
                return ''
            # print(1,head, rest)
            nx = transform_infix(rest)
            if is_atom(nx):
                return nx
            head, *rest = nx
            # print(2,head, rest)
            if rest == []:
                return head
        elif head == 'ie/neoteric':
            head, *rest = rest

    args, body = split_newline(rest)
    assert body == None
    cargs = [compile_expression(a, depth+1) for a in args]

    if head in infix_symbols:
        # print(head, cargs)
        r =  f" {head} ".join(cargs)
        if depth:
            return "(" + r + ")"
        else:
            return r
    elif head == "inc":
        assert len(cargs) == 1
        return f"{cargs[0]} += 1"
    else:
        return f"{head}({', '.join(cargs)})"


def split_on_commas(lst):
    r = [[]]
    for e in lst:
        if e == ',':
            r.append([])
        else:
            r[-1].append(e)
    return r


def transform_infix(x):
    if ',' in x:
        sections = split_on_commas(x)
    else:
        sections = [x]

    transformed_sections = []
    for section in sections:
        n = len(section)
        # print(x)
        # print(n)
        # print(n % 2)

        if n == 0:
            transformed_sections.append(section)
            continue
        elif n == 1:
            transformed_sections.append(section[0])
            continue
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

    n = len(transformed_sections)

    if n == 0:
        assert False
    elif n == 1:
        return transformed_sections[0]
    else:
        return transformed_sections



def split_newline(x):
    try:
        pos = x.index('ie/newline')
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
        # puts_expr(x)
        compile(x)

    for name in libs:
        name = name.strip('"')
        print(f"#include <{name}>")

    if libs:
        print()

    for e in top_level:
        print(e)
    if top_level:
        print()


    for name, spec in functions.items():
        if name == 'main':
            continue
        # pprint(spec)
        params, returns, body = spec
        print_func_decl(name, params, returns, ' ')
        print(';')
    if len(functions) > 1:
        print('\n')


    for name, spec in functions.items():
        # pprint(spec)
        params, returns, body = spec
        print_func_decl(name, params, returns)
        print(" ", end="")
        print_block(body, 1)
        print()
    print()

