import fileinput

from sys import argv
from pprint import pprint

input = None
indent = 0
indent_str = "    "
includes = []
functions = {}
infix_words = []
local_functions = {}
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

    print_file()

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
            }

    keywords = {
            'var': print_var,
            'let': print_let,
            'set': print_set,
            'while': print_while,
            }

    functions['getchar'] = [None, None, None]
    functions['putchar'] = [[int], None, None]

    global_variables['EOF'] = ['const', -1]

    infix_words = """
    =
    == !=
    +  +=
    -  -=
    *  *=
    /  /=
    && ||
    """.strip().split()


def print_file():
    for include in includes:
        print(include)

    print()

    for fn_name, fn_spec in local_functions.items():
        print_function_header(fn_name, *fn_spec)

    for fn_name, fn_spec in local_functions.items():
        print_function(fn_name, *fn_spec)


def print_function(fn_name, fn_args, fn_returns, fn_body):
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

    env = function_enviroment()
    print_block(fn_body, env)
    print()


def print_function_header(fn_name, fn_args, fn_returns, fn_body):
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
        print_indent()
        head = body[0]
        print_eval_stack(body, env)
        print("" if head in ['while'] else ";")


def print_indent():
    print(indent * indent_str, end="")


def include_lib(stack):
    lib_name = stack.pop()
    lib_name = lib_name[1:-1]
    includes.append(f"#include <{lib_name}>")


def parse_function(stack):
    global functions

    fn_name = get_word()
    args = None
    returns = None
    body = parse_until('end-fn')
    functions[fn_name] = ([args, returns, body])
    local_functions[fn_name] = ([args, returns, body])


def parse_until(end):
    body = []

    word = get_word()
    while word:
        if word ==end:
            break
        body.append(word)
        word = get_word()

    return body


def pluck_until(queue, end):
    body = []

    word = queue.pop(0)
    while word and word != end:
        body.append(word)
        word = queue.pop(0)

    return body


def print_var(queue, env):
    body = pluck_until(queue, "end-var")
    name, var_type, *init_val = body
    env[name] = ['var', var_type]
    print(f"{var_type} {name}", end="")
    if init_val and init_val != ['undef']:
        print(" = ", end="")
        print_eval_stack(init_val, env)


def print_let(queue, env):
    body = pluck_until(queue, "end-let")
    var_name, *stack = body
    print(f"{var_name} = ", end="")
    print_eval_stack(stack, env)
    assert len(stack) == 0


def print_set(queue, env):
    body = pluck_until(queue, "end-set")
    var_name, *stack = body
    print(f"{var_name} = ", end="")
    print_eval_stack(stack, env)




def print_while(queue, env):
    clause = pluck_until(queue, "do")
    body = pluck_until(queue, "end-while")
    # print(clause)
    # print(body)
    print("while (", end="")
    print_eval_stack(clause, env)
    print(") ", end="")
    print_block(body, env)


def print_eval_stack(input_stack, env):
    stack = []
    word = input_stack.pop(0)
    while word:
        val = parse_number(word)
        kw = keywords.get(word)
        spec = env.get(word)

        if val != None:
            stack.append(val)
        elif kw:
            kw(input_stack, env)
            return
        elif spec:
            type_name, *type_spec = spec
            if type_name == 'fn':
                args, returns, body = type_spec
                if args:
                    print(f"{word}(", end="")
                    for i in range(len(args)):
                        arg = stack.pop()
                        print(arg, end="")
                    print(f")", end="")
                else:
                    print(f"{word}()", end="")
                return
            elif type_name in ['var', 'const']:
                stack.append(word)
            elif type_name == 'infix':
                rhs = stack.pop()
                lhs = stack.pop()
                print(f"{lhs} {word} {rhs}", end="")
                return
            else:
                print(f"\n\n{word=} {type_name=}")
                assert False
        else:
            print("what is?", word)
            assert False

        word = input_stack.pop(0) if input_stack else None

    if len(stack) == 1:
        print(stack[0], end="")
        return

    assert len(stack) == 0


def print_word(word):
    print(f"{word}()", end="")


def new_env(env):
    e = {}
    e.update(env)
    return e


def function_enviroment():
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


if __name__ == "__main__":
    main()

