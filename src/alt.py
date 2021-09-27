code = """
double
  +
    + 1 2
    \ 3
""".strip()

indent_width = 2

# print("code:\n{}\n".format(code))
# print("#"*10)
# print("")

running = True

code_len = len(code)

i = 0

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
            # print("dedent", cmd);
        elif new_indent == indent:
            cmd = stack.pop()
            print(cmd)
            # print("newline", cmd);
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
        # print("word: {}".format(word))
        if stack[-1] == None:
            if word == "\\":
                stack.pop()
            else:
                stack[-1] = word
        else:
            # print("word: {}".format(word))
            print(word)
        # print("i1", i, repr(code[i:]))
        i = j
        # print("i2", i, repr(code[i:]))

    while i < code_len and code[i] == " ":
        i += 1

while stack:
    cmd = stack.pop()
    print(cmd)


