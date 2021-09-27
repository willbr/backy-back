code = """
: double
  * 2
double 10
.
""".strip()

indent_width = 2


running = True

code_len = len(code)

i = 0

imediate = [':']
break_chars = " \n"
indent = 0

stack = [None]

while i < code_len:
    # print("i", i, repr(code[i:]))
    j = i
    if code[j] == '\n':
        i += 1
        j += 1
        while j < code_len and code[j] == " ":
            j += 1
        delta = j - i
        if delta % 2 != 0:
            raise ValueError
        new_indent = delta / indent_width

        if new_indent == indent - 1:
            cmd = stack.pop()
            print(cmd)
            cmd = stack.pop()
            print(cmd)
            stack.append(None)
        elif new_indent == indent:
            cmd = stack.pop()
            print(cmd)
            stack.append(None)
        elif new_indent == indent + 1:
            stack.append(None)
        else:
            raise ValueError

        indent = new_indent

    else:
        while j < code_len and code[j] not in break_chars:
            j += 1
        word = code[i:j]
        if stack[-1] == None:
            if word == "\\":
                stack.pop()
            elif word in imediate:
                print(word)
                if word == ':':
                    stack[-1] = ";"
                else:
                    raise ValueError(word)
            else:
                stack[-1] = word
        else:
            print(word)
        i = j

    while i < code_len and code[i] == " ":
        i += 1

while stack:
    cmd = stack.pop()
    print(cmd)


