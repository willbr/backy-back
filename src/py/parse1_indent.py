import sys
import fileinput
from .tokenise import tokenise_file, tokenise_lines

class IndentParser():
    input_tokens = None
    new_indent = 0
    cur_indent = -1
    indent_width = 4
    next_token = None


    def __init__(self, tokens):
        self.input_tokens = tokens

    def read_token(self):
        if self.next_token:
            token = self.next_token
            self.next_token = None
            return token

        return next(self.input_tokens).strip('\n')


    def peek_token(self):
        if self.next_token:
            return self.next_token
        self.next_token = next(self.input_tokens).strip('\n')
        return self.next_token


    def push_token(self, t):
        if self.next_token:
            assert False
        self.next_token = t


    def tokens(self):
        syntax_stack = []

        try:
            yield('[')
            self.cur_indent = 0
            while True:
                token = self.read_token()
                if token == 'ie/newline':
                    if syntax_stack:
                        yield(syntax_stack)
                        assert False # unmatch syntax
                    yield(token)
                    token = self.peek_token()
                    while token == 'ie/newline':
                        _ = self.read_token()
                        token = self.peek_token()

                    if token[0] == ' ':
                        space_token = self.read_token()
                        spaces = len(space_token)
                        assert not spaces % self.indent_width
                        if self.peek_token() == 'ie/newline':
                            pass
                        else:
                            self.new_indent = spaces // self.indent_width
                    else:
                        self.new_indent = 0

                    diff = self.new_indent - self.cur_indent

                    if self.peek_token() == '\\':
                        if self.new_indent == self.cur_indent + 1:
                            _ = self.read_token()
                            self.push_token('ie/backslash')
                        else:
                            assert False
                    elif diff > 1:
                        assert False
                    elif diff == 1:
                        self.cur_indent += 1
                        yield('[')
                    elif diff == 0:
                        yield(']')
                        yield('[')
                    else:
                        for i in range(abs(diff)):
                            self.cur_indent -= 1
                            yield(']')
                        yield(']')
                        yield('[')
                elif token in '({[':
                    yield(token)
                    syntax_stack.append(token)

                elif token in ')}]':
                    open_char = syntax_stack.pop()

                    if open_char == '(':
                        assert token == ')'
                        yield(token)
                    elif open_char == '{':
                        assert token == '}'
                        yield(token)
                    elif open_char == '[':
                        assert token == ']'
                        yield(token)
                    else:
                        yield(token)
                        assert False
                else:
                    yield(token)

        except StopIteration:
            pass

        for i in range(self.cur_indent + 1):
            yield(']')


def parse_indent(tokens):
    ip = IndentParser(tokens)
    return ip.tokens()


if __name__ == '__main__':
    tokens = tokenise_file(sys.argv[1])
    tokens2 = parse_indent(tokens)
    print('\n'.join(tokens2))

