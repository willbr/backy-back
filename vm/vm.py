import math

print('hello')

msg = 'hello world'

type_number  = 0x1111_0000_0000_0001
type_string  = 0x1111_0000_0000_0002
type_command = 0xcccc_0000_0000_0001

id_return = 0
id_puts = 1
id_open_window = 12

def packed_string(s):
    data = s.encode('utf8')
    alignment = 8  # 64-bit alignment
    padding_size = (alignment - (len(data) % alignment)) % alignment
    aligned_data = data + b'\x00' * padding_size
    return [int.from_bytes(aligned_data[i:i + 8], byteorder='big', signed=False) for i in range(0, len(aligned_data), 8)]


def print_stack(stack):
    print(f"Stack contents: ({len(stack)})")
    i = len(stack) - 1  # Start from the back since type is on top
    while i >= 0:
        if stack[i] == type_number:
            print(f"Number: {stack[i - 1]}")
            i -= 2
        elif stack[i] == type_string:
            length = stack[i - 1]
            string_ints = stack[i - 2 - length:i - 2]
            string_value = b''.join(int.to_bytes(num, 8, byteorder='big', signed=False) for num in string_ints).rstrip(b'\0').decode('utf8')
            print(f"String: '{string_value}' (Length: {length*8})")
            i -= 2 + length
        else:
            print(f"Unknown Type Code: {stack[i]}")
            break
    if i != -1:  # If we didn't process the entire stack, we have an issue
        print(f"Stack integrity compromised: {i} items left unprocessed")

def ints_to_bytes(list_of_ints):
    data = b''.join(item.to_bytes(8, byteorder='big', signed=False) for item in list_of_ints)
    return data

def hex_dump(data):
    print("-" * 50)
    for offset in range(0, len(data), 16):
        row = data[offset:offset + 16]
        hex_values = " ".join(f"{byte:02x}" for byte in row)
        ascii_values = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in row)
        print(f"{offset:08x}  {hex_values:<47}  {ascii_values}")
    print("-" * 50)

def push_number(stack, value):
    stack.extend([value, type_number])

def pop_number(stack):
    if len(stack) < 2 or stack[-1] != type_number:
        raise ValueError("Expected a number on stack")
    stack.pop()  # Remove the type
    return stack.pop()  # Remove and return the value

def push_string(stack, string):
    encoded_string = string.encode("utf-8")
    string_length = len(encoded_string)
    aligned_string_length = math.ceil(string_length / 8) * 8
    padded_string = encoded_string.ljust(aligned_string_length, b'\0')
    string_ints = [int.from_bytes(padded_string[i:i+8], byteorder='big', signed=False) for i in range(0, aligned_string_length, 8)]
    stack.extend([*string_ints, len(string_ints), type_string])

def pop_string(stack):
    if len(stack) < 3 or stack[-1] != type_string:
        raise ValueError("Expected a string on stack")
    stack.pop()  # Remove the type
    length = stack.pop()  # Pop length
    string_ints = [stack.pop() for _ in range(length)][::-1]  # Pop string data
    string_value = b''.join(int.to_bytes(num, 8, byteorder='big', signed=False) for num in string_ints).rstrip(b'\0').decode('utf8')
    return string_value

def call_command(stack, cmd_id):
    #print(f'call command {cmd_id=}')
    if cmd_id == id_open_window:
        h = pop_number(stack)
        w = pop_number(stack)
        print(f'open_window {w=}, {h=}')
    elif cmd_id == id_puts:
        s = pop_string(stack)
        print(s)
    else:
        assert False, f'invalid cmd {cmd_id}'

packed_msg = packed_string(msg)
#print(f'{packed_msg=}')

byte_code = [
    type_string, len(packed_msg), *packed_msg,
    type_command, id_puts,
    type_number, 640,
    type_number, 480,
    type_command, id_open_window,
    type_command, id_return,
]

print('byte_code=')
hex_dump(ints_to_bytes(byte_code))
stack = []  # Use a list as our stack

#print_stack(stack)

# instruction pointer
i = 0

while i < len(byte_code):
    #print()
    op = byte_code[i]
    i += 1
    #print_stack(stack)
    #hex_dump(stack)

    if op == type_number:
        n = byte_code[i]
        i += 1
        push_number(stack, n)

    elif op == type_string:
        packed_len = byte_code[i]
        i += 1
        string_ints = byte_code[i:i + packed_len]
        string_value = b''.join(int.to_bytes(j, 8, byteorder='big', signed=False) for j in string_ints).rstrip(b'\0').decode('utf8')
        i += packed_len
        push_string(stack, string_value)

    elif op == type_command:
        cmd_id = byte_code[i]
        assert cmd_id >= 0
        i += 1

        if cmd_id == id_return:
            print('return')
            break

        call_command(stack, cmd_id)

    else:
        assert False, f'unknown op: {op}'

if stack != []:
    print_stack(stack)
    hex_dump(ints_to_bytes(stack))

