import fileinput
from dataclasses import dataclass

@dataclass
class Command:
    cmd: str
    args: int
    reduce: bool

stack = [Command(None, 0, False)]

for line in fileinput.input():
    word = line.strip()
    # print("w", word)

    c = stack[-1]

    if word == "indent":
        if c.reduce and c.args > 1:
            print("r1", c)
        stack.append(Command(None, 0, False))
        continue
    elif word == "dedent":
        print("<dedent")
        c = stack.pop()
        print(c.cmd)
        print("dedent>")
        continue
    elif word == "newline":
        print("<newline")
        print( stack.pop().cmd)
        print("newline>")
        stack.append(Command(None, 0, False))
        continue

    if c.cmd == None:
        c.cmd = word
        c.reduce = word in ['+', '-', '*', '/']
    else:
        print("w   ", word)
        if c.reduce and c.args > 1:
            print("r3", c)
        c.args += 1

while stack:
    print(stack.pop().cmd)

