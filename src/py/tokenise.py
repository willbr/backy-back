import fileinput
import textwrap
import sys


class Tokeniser():
    file = None
    i = 0
    line = ""
    len_line = 0
    next_token = None
    breakchars = " \t\n,;()[]{}"

    def __init__(self, filename):
        self.file = fileinput.input(filename)

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


    def read_string(self):
        start_pos = self.i
        assert self.line[self.i] == '"'
        self.i += 1

        while self.i < self.len_line and self.line[self.i] not in '"':
            self.i += 1

        assert self.line[self.i] == '"'

        self.i += 1
        word = self.line[start_pos:self.i]
        return word


    def read_token(self):
        start_pos = self.i
        while self.i < self.len_line and self.line[self.i] not in self.breakchars:
            self.i += 1

        len_word = self.i - start_pos
        assert len_word
        word = self.line[start_pos:self.i]

        next_char = self.line[self.i]

        if next_char in '({[':
            self.next_token = word
            word = "ie/neoteric"

        return word


    def next_word(self):
        if self.next_token:
            word = self.next_token
            self.next_token = None
            return word

        if self.i >= self.len_line:
            self.get_line()

        if self.line[self.i] == '\n':
            self.get_line()
            self.chomp(' ')
            self.next_token = ' ' * self.i
            word = 'ie/newline'

        elif self.line[self.i] == '"':
            word = self.read_string()

        elif self.line[self.i] == '\t':
            assert False

        elif self.line[self.i] in self.breakchars:
            word = self.line[self.i]
            self.i += 1

            if word == ',':
                if self.line[self.i] not in ' \n':
                    self.die("comma must be followed by white space")
            elif word in ')}]':
                if self.line[self.i] not in ' \n)}]':
                    die("close marker must be followed by another close marker or whitespace")

        else:
            word = self.read_token()

        self.chomp(' ')
        return word


    def die(self, msg):
        l = line.strip()
        red = '\u001b[31m'
        white = '\u001b[37m'
        bg_red = '\u001b[41m'
        reset = '\u001b[0m'
        print(textwrap.dedent(f"""

        {bg_red}ERROR: {white}{msg}{reset}

        {l[:i]}{red}{l[i]}{reset}{l[i+1:]}
        {" "*i}^

        """), file=sys.stderr)
        exit(1)


def main():
    filename = sys.argv[1]
    t = Tokeniser(filename)
    tokens  = t.read_tokens()
    print('\n'.join(tokens))


if __name__ == "__main__":
    main()

