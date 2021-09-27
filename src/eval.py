import fileinput

stack = []
env = {}

input = fileinput.input()
while True:
    token = input.readline().strip()
    print(stack)
    print(token)

    try:
        i = int(token)
        stack.append(i)
        continue
    except ValueError:
        pass

    if token == '+':
        n2 = stack.pop()
        n1 = stack.pop()
        stack.append(n1 + n2)
    elif token == '*':
        n2 = stack.pop()
        n1 = stack.pop()
        stack.append(n1 * n2)
    elif token == 'double':
        n1 = stack.pop()
        stack.append(n1 * 2)
    elif token == ":":
        print("ere")
        name = input.readline().strip()
        token = input.readline().strip()
        body = []
        while token != ";" and token != '':
            body.append(token)
            token = input.readline().strip()
        print(name, body)
    else:
        raise ValueError(token)

