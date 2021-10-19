import fileinput

from sys import argv
from pprint import pprint

input = None
indent = 0
indent_str = "    "
top_level = []
functions = {}
infix_words = []
global_variables = {}
keywords = {}
parsers = {}


def main():
    global input
    input = fileinput.input(argv[1])

    stack = []

    init()

    word = get_word()
    while word:
        p = parsers.get(word)
        if p:
            p(stack)
        else:
            stack.append(word)

        word = get_word()

    env = file_enviroment()

    print_file(env)

    assert len(stack) == 0


def init():
    global parsers
    global keywords
    global functions
    global global_variables
    global infix_words

    parsers = {
            'fn': parse_function,
            'include-lib': include_lib,
            'define': parse_define,
            }

    keywords = {
            'var': print_var,
            'let': print_let,
            'set': print_set,
            'while': print_while,
            'for':   print_for,
            }

    functions['getchar'] = [None, None, None]
    functions['putchar'] = [["int"], None, None]
    functions['printf'] = [["cstring", "vargs"], None, None]

    global_variables['EOF'] = ['const', -1]

    infix_words = """
    =
    == !=
    +  +=
    -  -=
    *  *=
    /  /=
    <  <=
    >  >=
    && ||
    """.strip().split()


def print_file(env):
    first_fn = None
    for statement in top_level:
        head, *tail = statement
        if head == "include-lib":
            assert len(tail) == 1
            filename = tail[0]
            print(f"#include <{filename}>")
        elif head == "define":
            name, val = tail
            env[name] = ['define', name, val]
            print(f"#define {name} = {val}")
        elif head == "fn":
            fn_name, *fn_spec = tail
            print_function_header(env, fn_name, *fn_spec)
        else:
            print(head)
            assert False

    for statement in top_level:
        head, *tail = statement
        if head == 'fn':
            fn_name, *fn_spec = tail
            print_function(env, fn_name, *fn_spec)


def print_function(env, fn_name, fn_args, fn_returns, fn_body):
    global indent

    if fn_returns:
        assert False
    else:
        print("void")

    print(fn_name, end="")

    if fn_args:
        assert False
    else:
        print("(void) ", end="")

    print_block(fn_body, env)
    print()


def print_function_header(env, fn_name, fn_args, fn_returns, fn_body):
    if fn_name == 'main':
        return

    assert False


def print_block(body, parent_env):
    global indent

    body_queue = body[:]

    env = new_env(parent_env)

    indent += 1
    print("{")

    print_statements(body, env)

    indent -= 1
    print_indent()
    print("}", end="")


def print_statements(body, env):
    while body:
        head = body[0]
        end = "end-" + head
        statement = pluck_until(body, end)
        print_indent()
        print_statement(statement, env)
        print("" if head in ['while'] else ";")


def print_statement(statement, env):
    head, *tail = statement

    if kw := keywords.get(head):
        kw(tail, env)
    elif e := env.get(head):
        e_type, *spec = e
        if e_type == 'fn':
            params, returns, body = spec
            args = tail
            print(f"{head}(", end="")
            eargs = eval_stack(args, env)
            print(', '.join(eargs), end="")
            print(")", end="")
        else:
            assert False
    else:
        assert False


def print_indent():
    print(indent * indent_str, end="")


def include_lib(stack):
    body = parse_until("end-include-lib")
    assert len(body) == 1
    lib_name = body[0]
    top_level.append(["include-lib", lib_name])


def parse_function(stack):
    global functions

    fn_name = get_word()
    args = None
    returns = None
    body = parse_until('end-fn')
    functions[fn_name] = ([args, returns, body])
    top_level.append(["fn", fn_name, args, returns, body])


def parse_until(end):
    body = []

    word = get_word()
    while word:
        if word == end:
            break
        body.append(word)
        word = get_word()

    assert word == end

    return body


def pluck_until(queue, end):
    body = []

    word = queue.pop(0)
    while word and word != end:
        body.append(word)
        word = queue.pop(0)

    return body


def print_var(queue, env):
    name, var_type, *init_val = queue
    env[name] = ['var', var_type]
    print(f"{var_type} {name}", end="")
    if init_val and init_val != ['undef']:
        ev = eval_stack(init_val, env)
        assert len(ev) == 1
        print(f" = {ev[0]}", end="")


def print_let(queue, env):
    body = pluck_until(queue, "end-let")
    var_name, *stack = body
    print(f"{var_name} = ", end="")
    print_eval_stack(stack, env)
    assert len(stack) == 0


def print_set(queue, env):
    var_name, *stack = queue
    print(f"{var_name} = ", end="")
    estack = eval_stack(stack, env)
    print(', '.join(estack), end="")
    assert len(stack) == 0


def print_while(queue, env):
    clause = pluck_until(queue, "do")
    print("while (", end="")
    eclause = eval_stack(clause, env)
    print(', '.join(eclause), end="")
    print(") ", end="")
    print_block(queue, env)


def print_for(queue, env):
    clause = pluck_until(queue, "do")
    body = pluck_until(queue, "end-for")
    # print(clause)
    # print(body)
    print("for (", end="")
    # print(clause)
    while clause:
        print_eval_stack(clause, env)
        if clause:
            print(", ", end="")
    print(") ", end="")
    print_block(body, env)


def print_eval_stack(input_stack, env):
    assert False


def eval_stack(input_stack, env):
    stack = []
    word = input_stack.pop(0)
    while word:
        val = parse_number(word)
        kw = keywords.get(word)
        spec = env.get(word)

        if val != None:
            stack.append(val)
        elif word[0] == '"':
            stack.append(word)
        elif kw:
            kw(input_stack, env)
        elif spec:
            type_name, *type_spec = spec
            if type_name == 'fn':
                args, returns, body = type_spec
                if args:
                    r = []
                    r.append(f"{word}(")
                    for i in range(len(args)):
                        arg = stack.pop()
                        r.append(arg)
                    r.append(")")
                    stack.append(''.join(r))
                else:
                    stack.append(f"{word}()")
            elif type_name in ['var', 'const']:
                stack.append(word)
            elif type_name == 'infix':
                rhs = stack.pop()
                lhs = stack.pop()
                r = f"{lhs} {word} {rhs}"
                stack.append(f"({r})")
            elif type_name == 'define':
                stack.append(word)
            else:
                print(f"\n\n{word=} {type_name=}")
                assert False
        else:
            print("what is?", word)
            assert False

        word = input_stack.pop(0) if input_stack else None

    return stack


def print_word(word):
    print(f"{word}()", end="")


def new_env(env):
    e = {}
    e.update(env)
    return e


def file_enviroment():
    e = {}
    e.update(global_variables)

    for word in infix_words:
        e[word] = ['infix']

    for fn_name, spec in functions.items():
        e[fn_name] = ['fn', *spec]

    return e

def get_word():
    get_line()
    return line_buffer.strip()


def get_line():
    global line_buffer
    line_buffer = input.readline()


def parse_number(word):
    try:
        i = int(word)
        return i
    except:
        pass

    try:
        f = float(word)
        return f
    except:
        pass


def parse_define(stack):
    body = parse_until('end-define')
    name, *initial_value = body
    top_level.append(['define', *body])


if __name__ == "__main__":
    main()

