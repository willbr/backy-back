import ctypes
import math

print('hello')

msg = 'hello world'

type_number  = 0x1111000000000001
type_string  = 0x1111000000000002
type_command = 0xcccc000000000001

id_return = 0
id_puts = 1
id_open_window = 12

def packed_string(s):
    data = s.encode('utf8')
    alignment = ctypes.sizeof(ctypes.c_int64)
    padding_size = (alignment - (len(data) % alignment)) % alignment
    aligned_data = data + b'\x00' * padding_size
    return [
            int.from_bytes(aligned_data[i:i + 8], byteorder='big', signed=True)
            for i in range(0, len(aligned_data), 8)
        ]

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

#print(f'{byte_code=}')
print('byte_code=')
for n in byte_code:
    print(f'{n:016x} {n:4d}')


class Stack(ctypes.Structure):
    _fields_ = [
        ("base", ctypes.POINTER(ctypes.c_int64)),  # int *base;
        ("top", ctypes.POINTER(ctypes.c_int64)),   # int *top;
        ("end", ctypes.POINTER(ctypes.c_int64))    # int *end;
    ]


def print_stack(stack):
    TYPE_STRING = 1
    TYPE_NUMBER = 2

    print("Stack contents:")
    pointer = stack.top

    # Use ctypes.addressof for pointer comparisons
    while ctypes.addressof(pointer.contents) > ctypes.addressof(stack.base.contents):
        # Decrement pointer by one `c_int64`
        pointer = ctypes.cast(ctypes.addressof(pointer.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
        type_code = pointer.contents.value

        if type_code == TYPE_STRING:
            # Move to the string length
            pointer = ctypes.cast(ctypes.addressof(pointer.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
            string_length = pointer.contents.value

            # Calculate aligned length and move to string data
            aligned_length = (string_length + ctypes.sizeof(ctypes.c_int64) - 1) // ctypes.sizeof(ctypes.c_int64)
            pointer = ctypes.cast(ctypes.addressof(pointer.contents) - aligned_length * ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_char))

            # Read the string
            string_data = (ctypes.c_char * string_length).from_address(ctypes.addressof(pointer.contents)).value.decode('utf-8')
            print(f"String: '{string_data}' (Length: {string_length})")

        elif type_code == TYPE_NUMBER:
            # Move to the number
            pointer = ctypes.cast(ctypes.addressof(pointer.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
            number = pointer.contents.value
            print(f"Number: {number}")

        else:
            print(f"Unknown Type Code: {type_code}")
            break


def hex_dump(stack):
    # Calculate the number of bytes in the stack
    total_bytes = ctypes.addressof(stack.top.contents) - ctypes.addressof(stack.base.contents)

    print("Hex Dump of Stack:")
    print("-" * 50)
    base_address = ctypes.addressof(stack.base.contents)
    for offset in range(0, total_bytes, 16):  # 16 bytes per row
        row_address = base_address + offset
        row_data = (ctypes.c_ubyte * 16).from_address(row_address)
        hex_values = " ".join(f"{byte:02x}" for byte in row_data[:min(16, total_bytes - offset)])
        ascii_values = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in row_data[:min(16, total_bytes - offset)])
        print(f"{row_address:016x}  {hex_values:<47}  {ascii_values}")
    print("-" * 50)

def hex_dump(stack):
    total_bytes = ctypes.addressof(stack.top.contents) - ctypes.addressof(stack.base.contents)

    print("Hex Dump of Stack:")
    print("-" * 50)
    base_address = ctypes.addressof(stack.base.contents)
    for offset in range(0, total_bytes, 16):  # 16 bytes per row
        row_address = base_address + offset
        row_data = (ctypes.c_ubyte * 16).from_address(row_address)
        hex_values = " ".join(f"{byte:02x}" for byte in row_data[:min(16, total_bytes - offset)])
        ascii_values = "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in row_data[:min(16, total_bytes - offset)])
        print(f"{row_address:016x}  {hex_values:<47}  {ascii_values}")
    print("-" * 50)


def push_number(stack, value):
    # Define a type code for numbers (use any unique identifier, e.g., 2)
    TYPE_NUMBER = 2

    # Calculate space required: value + type code
    alignment = ctypes.sizeof(ctypes.c_int64)
    required_space = alignment + alignment

    # Calculate available space
    available_space = (ctypes.addressof(stack.end.contents) - ctypes.addressof(stack.top.contents))
    if required_space > available_space:
        raise OverflowError("Stack overflow: not enough space to push the number")

    # Push the number
    stack.top.contents.value = value
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) + alignment, ctypes.POINTER(ctypes.c_int64))

    # Push the type code
    stack.top.contents.value = TYPE_NUMBER
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) + alignment, ctypes.POINTER(ctypes.c_int64))


def pop_number(stack):
    TYPE_NUMBER = 2

    # Check the type code
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
    type_code = stack.top.contents.value

    if type_code != TYPE_NUMBER:
        raise ValueError(f"Expected type code {TYPE_NUMBER} for a number, but got {type_code}")

    # Pop the number
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
    number = stack.top.contents.value

    return number


def push_string(stack, string):
    # Define a type code for strings (use any unique identifier, e.g., 1)
    TYPE_STRING = 1

    # Convert the string to its bytes representation
    encoded_string = string.encode("utf-8")
    string_length = len(encoded_string)

    # Align the string length to the nearest multiple of word size
    alignment = ctypes.sizeof(ctypes.c_int64)  # Assume alignment for int64
    aligned_string_length = math.ceil(string_length / alignment) * alignment

    # Calculate the total space required: aligned string + length + type code
    required_space = aligned_string_length + alignment + alignment

    # Calculate available space
    available_space = (ctypes.addressof(stack.end.contents) - ctypes.addressof(stack.top.contents))
    if required_space > available_space:
        raise OverflowError("Stack overflow: not enough space to push the string")

    # Copy the string data into the stack
    ctypes.memmove(ctypes.addressof(stack.top.contents), encoded_string, string_length)

    # Adjust the `top` pointer after the aligned string
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) + aligned_string_length, ctypes.POINTER(ctypes.c_int64))

    # Push the length of the string
    stack.top.contents.value = string_length
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) + alignment, ctypes.POINTER(ctypes.c_int64))

    # Push the type code for the string
    stack.top.contents.value = TYPE_STRING
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) + alignment, ctypes.POINTER(ctypes.c_int64))



def pop_string(stack):
    TYPE_STRING = 1

    # Check the type code
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
    type_code = stack.top.contents.value

    if type_code != TYPE_STRING:
        raise ValueError(f"Expected type code {TYPE_STRING} for a string, but got {type_code}")

    # Get the string length
    stack.top = ctypes.cast(ctypes.addressof(stack.top.contents) - ctypes.sizeof(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64))
    string_length = stack.top.contents.value

    # Calculate aligned length
    aligned_length = (string_length + ctypes.sizeof(ctypes.c_int64) - 1) // ctypes.sizeof(ctypes.c_int64)

    # Get the string data without modifying stack.top to an incompatible type
    string_data_address = ctypes.addressof(stack.top.contents) - aligned_length * ctypes.sizeof(ctypes.c_int64)
    string_data = (ctypes.c_char * string_length).from_address(string_data_address).value.decode('utf-8')

    # Update the stack pointer after popping the string
    stack.top = ctypes.cast(string_data_address, ctypes.POINTER(ctypes.c_int64))

    return string_data


def call_command(stack, cmd_id):
    print(f'call command {cmd_id=}')
    if cmd_id == id_open_window:
        h = pop_number(stack)
        w = pop_number(stack)
        print(f'open_window {w=}, {h=}')
    elif cmd_id == id_puts:
        s = pop_string(stack)
        print(s)
    else:
        assert False, 'invalid cmd {cmd_id}'


array_size = 100  # Define the size of the array
array = (ctypes.c_int64 * array_size)(*([0] * array_size))  # Initialize to zero

stack = Stack()
stack.base = ctypes.cast(array, ctypes.POINTER(ctypes.c_int64))  # Point to the start of the array
stack.top = stack.base  # Current pointer also starts at the first element
stack.end = ctypes.cast(ctypes.addressof(array) + ctypes.sizeof(ctypes.c_int64) * array_size, ctypes.POINTER(ctypes.c_int64))  # Point 1 past the end

print_stack(stack)

# instruction pointer
i = 0

while i < len(byte_code):
    print()
    op = byte_code[i]
    i += 1
    #print(f'// {op=}')
    print_stack(stack)
    #hex_dump(stack)

    if op == type_number:
        n = byte_code[i]
        i += 1
        push_number(stack, n)

    elif op == type_string:
        packed_len = byte_code[i]
        i += 1
        string_ints = byte_code[i:i + packed_len]
        string_data = b''.join(j.to_bytes(8, byteorder='big', signed=True) for j in string_ints)
        i += packed_len
        string_value = string_data.decode('utf8')
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

print_stack(stack)
hex_dump(stack)

