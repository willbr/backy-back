import fileinput

stack = []

for line in fileinput.input():
    word = line.strip()
    print(stack)
    print(word)

    try:
        i = int(word)
        stack.append(i)
        continue
    except ValueError:
        pass

    if word == '+':
        n2 = stack.pop()
        n1 = stack.pop()
        stack.append(n1 + n2)
    elif word == '*':
        n2 = stack.pop()
        n1 = stack.pop()
        stack.append(n1 * n2)
    elif word == 'double':
        n1 = stack.pop()
        stack.append(n1 * 2)
    else:
        raise ValueError(word)

print(stack)

