from parse2_syntax import parse_file, is_atom, remove_newline, puts_expr
from pprint import pprint

libs = set()
types = {
        'char': 'short',
        'short': 'short',
        'int': 'int',
        'long': 'long',
        }
structs = {}
functions = {}
global_vars = {}
top_level = []
infix_symbols = """
= := == !=
+ += - -= * *= / /=
> >= < <=
and or
""".split()


def compile(x):
    head, *args = x
    if head == 'def':
        compile_proc(*args)
    elif head == 'func-decl':
        compile_func_decl(*args)
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
    elif head == 'comment':
        top_level.append(compile_comment(*args))
    elif head == 'ie/newline':
        assert args == []
    else:
        print(head)
        assert False


def compile_comment(*args):
    print(1, args)
    first_line, rest = split_newline(args)
    comment_body = [repr(first_line)]
    for line in rest:
        comment_body += repr(line)
    #todo escape */ in comment body
    comment = '/* ' + ' '.join(comment_body) + ' */'
    return comment


def mangle(name):
    return name.replace('-', '_')


def compile_define(*args):
    first_line, body = split_newline(args)
    sep   = ""
    dbody = ""
    if body != ():
        assert False
    n = len(first_line)
    if n == 1:
        define_name = first_line[0]
    elif n == 2:
        define_name = first_line[0]
        sep = " "
        dbody = first_line[1]
    else:
        assert False
    decl = f"#define {define_name}{sep}{dbody}"
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
    assert body[0] == 'ie/newline'
    body = body[1:]
    assert len(body) == 0
    libs.add(lib_name)
    name = lib_name.strip('"')
    clib = f"#include <{name}>"
    top_level.append(clib)



def compile_func_decl(fn_name, *spec):
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

    if body:
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

    functions[fn_name] = [params, returns, body]


def compile_proc(fn_name, *spec):
    if not is_atom(fn_name):
        if fn_name[0] == 'ie/neoteric':
            assert len(fn_name) == 3
            raw_params = fn_name[2]
            fn_name    = fn_name[1]
        else:
            assert False

    [params, returns, body] = functions[fn_name]

    cbody = [compile_statement(x) for x in body]

    functions[fn_name] = [params, returns, cbody]


def compile_params(spec):
    if spec[0] == 'ie/newline':
        spec = spec[1:]

    params = []
    for param in spec:
        n = len(param)
        if len(param) == 3:
            assert param.pop() == 'ie/newline'

        if n == 1:
            if param[0] == 'void':
                params.append('void')
            else:
                print(param)
                assert False
        else:
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
    elif head == ':=':
        return compile_let(args, body) + ";"
    elif head == 'if':
        return compile_if(args, body)
    elif head == 'comment':
        print(head,args,body)
        return compile_comment(*args, *body)

    assert body == [] or body == ()
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


def compile_let(args, body):
    assert body == []
    num_args = len(args)
    assert num_args == 2
    var_name, x = args
    var_type = infer_type(x)
    var_val = compile_expression(x)
    if x[0] == 'ie/neoteric':
        _, cmd, arg = x
        if cmd in types.keys():
            if cmd == var_type:
                var_val = compile_expression(arg)
    return f"{var_type} {var_name} = {var_val}"


def infer_type(x):
    if is_atom(x):
        assert False

    n = len(x)
    head, *rest = x
    if head == 'ie/neoteric':
        cmd = rest[0]
        if cmd in types.keys():
            return cmd
        params, returns, body = functions[cmd]
        return returns
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
    assert body == ()
    cargs = [compile_expression(a, depth+1) for a in args]

    if head in infix_symbols:
        # print(head, cargs)
        r =  f" {head} ".join(cargs)
        if depth:
            return "(" + r + ")"
        else:
            return r
    elif head in types.keys():
        return f"({head})({', '.join(cargs)})"
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
        rhs = ()
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
        head, *args = x
        if head in ['def', 'func-decl']:
            compile_func_decl(*args)

    for x in prog:
        # puts_expr(x)
        compile(x)

    for e in top_level:
        print(e)
    if top_level:
        print()


    func_decls = 0
    for name, spec in functions.items():
        if name == 'main':
            continue
        # pprint(spec)
        params, returns, body = spec
        if body == ():
            continue
        print_func_decl(name, params, returns, ' ')
        print(';')
        func_decls += 1
    if func_decls:
        print('\n')


    for name, spec in functions.items():
        # pprint(spec)
        params, returns, body = spec
        if body == ():
            continue
        print_func_decl(name, params, returns)
        print(" ", end="")
        print_block(body, 1)
        print()

