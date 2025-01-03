

print('hello')

msg = 'hello world'

type_number  = 1
type_string  = 2
type_command = 1001

id_return = 0
id_puts = 1
id_open_window = 12

byte_code = [
    type_string, len(msg), *msg.encode('utf8'),
    type_command, id_puts, 1,
    type_number, 640,
    type_number, 480,
    type_command, id_open_window, 2,
    type_command, id_return, 0,
]

print(f'{byte_code=}')

stack = []

cmds = {
    id_puts: lambda s: print(s),
    id_open_window: lambda w, h: print(f'open-window({w=}, {h=})'),
}


# instruction pointer
i = 0

# eval

while i < len(byte_code):
    print(f'{stack=}')

    op = byte_code[i]
    i += 1
    print(f'{op=}')

    if op == type_number:
        n = byte_code[i]
        i += 1
        stack.append(n)

    elif op == type_string:
        string_len = byte_code[i]
        i += 1
        string_data = byte_code[i:i + string_len]
        i += string_len
        string_value = bytes(string_data).decode('utf8')
        stack.append(string_value)
        print(f"Pushed string: {string_value=}")

    elif op == type_command:
        cmd_id = byte_code[i]
        assert cmd_id >= 0
        i += 1

        number_args = byte_code[i]
        assert number_args >= 0
        i += 1

        if cmd_id == id_return:
            break

        fn = cmds.get(cmd_id, None)
        assert fn != None, f'unknown {cmd_id=}'

        args = stack[-number_args:]
        stack = stack[:-number_args]

        fn(*args)

    else:
        assert False, f'unknown op: {op}'

print(f'Stack after operation: {stack=}')

