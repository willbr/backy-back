import re

def tokenize(code):
    token_pattern = r'[^\s()\[\],]+|[\(\)\[\],]'
    tokens = []
    lines = code.split('\n')
    for lineno, line in enumerate(lines):
        line = line.split('#')[0]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(' '))
        line_tokens = re.findall(token_pattern, line.strip())
        line_tokens = [
            unescape_string(token) if token.startswith('"') and token.endswith('"') else token
            for token in line_tokens
        ]
        tokens.append((indent, line_tokens))
    return tokens

def unescape_string(s):
    s = s[1:-1]
    s = s.encode('utf-8').decode('unicode_escape')
    return '"' + s + '"'

def parse_line(tokens):
    INFIX_OPERATORS = {'=', '+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=', 'and', 'or'}

    def parse_expression(tokens, pos):
        expr = []
        while pos < len(tokens):
            token = tokens[pos]
            if token == '[':
                sub_expr, pos = parse_expression(tokens, pos + 1)
                expr.append(sub_expr)
            elif token == ']':
                return expr, pos + 1
            else:
                expr.append(token)
                pos += 1
        return expr, pos

    expr, _ = parse_expression(tokens, 0)

    if expr[0] == 'infix':
        return expr
    elif expr[0] == 'fn':
        return expr
    elif expr[0] == 'when':
        condition_expr = expr[1:]
        if any(op in condition_expr for op in INFIX_OPERATORS):
            condition_expr = ['infix'] + condition_expr
        return ['when', condition_expr]
    else:
        if any(op in expr for op in INFIX_OPERATORS):
            return ['infix'] + expr
        else:
            return expr

def parse(tokens):
    pos = 0
    def parse_block(indent, is_sub_block=False):
        nonlocal pos
        block = []
        while pos < len(tokens):
            current_indent, line_tokens = tokens[pos]
            if current_indent < indent: # The block ends here
                break
            elif current_indent > indent:
                raise SyntaxError(f"Unexpected indentation at line {pos + 1}")
            else:
                pos += 1
                parsed_line = parse_line(line_tokens)
                if pos < len(tokens) and tokens[pos][0] > current_indent:
                    sub_block = parse_block(tokens[pos][0], is_sub_block=True)
                    parsed_line.append(sub_block)
                block.append(parsed_line)
        if is_sub_block:
            return ['block'] + block
        else:
            return block
    return parse_block(0)

# Example usage
code = """
infix 1 + 2 + 3.1
.s
puts
# This is a comment
a = 5
puts a

fn double
    dup
    $ + $

puts "before"
puts [double 10]
puts "after"

when a > 1
    puts "big"

puts "end"
"""

expected_ast = [
    ['infix', '1', '+', '2', '+', '3.1'],
    ['.s'],
    ['puts'],
    ['infix', 'a', '=', '5'],
    ['puts', 'a'],
    ['fn', 'double', [
        'block',
        ['dup'],
        ['infix', '$', '+', '$'],
    ]],
    ['puts', '"before"'],
    ['puts', ['double', '10']],
    ['puts', '"after"'],
    ['when', ['infix', 'a', '>', '1'], [
        'block',
        ['puts', '"big"'],
    ]],
    ['puts', '"end"'],
]

from pprint import pprint
tokens = tokenize(code)
print("Tokens:")
pprint(tokens)

ast = parse(tokens)
print("\nAST:")
pprint(ast)

assert ast == expected_ast

