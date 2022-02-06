import fileinput
import textwrap
import sys
from rich import print
from rich.markup import escape


class Tokeniser():
    file = None
    i = 0
    line = ""
    len_line = 0
    next_token = None
    breakchars = " \t\n,;()[]{}"
    prefix = {}

    def __init__(self):
        self.prefix['"'] = read_string
        pass


    def __del__(self):
        self.file.close()


    def read_tokens(self):
        try:
            while True:
                w = self.next_word()
                yield w
        except StopIteration:
            pass


    def get_line(self):
        self.line = next(self.file)
        self.len_line = len(self.line)
        self.i = 0


    def chomp(self, chars):
        while self.i < self.len_line and self.line[self.i] in chars:
            self.i += 1


    def read_token(self):
        start_pos = self.i
        while self.i < self.len_line and self.line[self.i] not in self.breakchars:
            self.i += 1

        len_word = self.i - start_pos
        assert len_word
        word = self.line[start_pos:self.i]

        next_char = self.line[self.i]

        if next_char in '({[':
            self.push_token(word)
            word = "ie/neoteric"

        return word


    def push_token(self, token):
        if self.next_token != None:
            print(repr(token))
            print(repr(self.next_token))
            assert False
        self.next_token = token


    def next_word(self):
        if self.next_token:
            word = self.next_token
            self.next_token = None
            return word

        if self.i >= self.len_line:
            self.get_line()

        prefix_fn = self.prefix.get(self.line[self.i], None)

        if self.line[self.i] == '\n':
            self.get_line()
            self.chomp(' ')
            if self.i > 0:
                self.push_token(' ' * self.i)
            word = 'ie/newline'

        elif self.line[self.i] == '\t':
            assert False

        elif prefix_fn:
            word = prefix_fn(self)

        elif self.line[self.i] in self.breakchars:
            word = self.line[self.i]
            self.i += 1

            try:
                next_char = self.line[self.i]
            except IndexError:
                next_char = ''

            if word == '[':
                self.push_token("ie/prefix")
            elif word == ',':
                if next_char not in ' \n':
                    self.die("comma must be followed by white space")
            elif word in ')}]':
                if next_char not in ' ,\n)}]':
                    self.die("close marker must be followed by another close marker, comma  or whitespace")

        else:
            word = self.read_token()

        self.chomp(' ')
        return word

    def die(self, msg):
        l = self.line.strip()
        i = self.i
        err_msg =textwrap.dedent(f"""
        {msg}
        {l}
        {" "*i}^
        """).strip()
        raise SyntaxError(err_msg)


def read_string(t):
    start_pos = t.i
    assert t.line[t.i] == '"'
    t.i += 1

    while t.i < t.len_line and t.line[t.i] not in '"':
        t.i += 1

    assert t.line[t.i] == '"'

    t.i += 1
    word = t.line[start_pos:t.i]
    return word


def tokenise_file(filename):
    t = Tokeniser()
    t.file = fileinput.input(filename)
    tokens  = t.read_tokens()
    return tokens


def tokenise_lines(lines):
    t = Tokeniser()
    t.file = (line for line in lines)
    tokens  = t.read_tokens()
    return tokens


if __name__ == "__main__":
    filename = sys.argv[1]
    try:
        tokens  = tokenise_file(filename)
        print('\n'.join(tokens))
    except SyntaxError as e:
        print(f"[r]ERROR:[/] {escape(str(e))}")

