import ctypes

# Load the DLL
vm = ctypes.CDLL('./vm.dll')

# Define the Stack structure
class Stack(ctypes.Structure):
    _fields_ = [
        ("stack", ctypes.c_int64 * 1024),
        ("top", ctypes.POINTER(ctypes.c_int64)),
        ("end", ctypes.POINTER(ctypes.c_int64)),
        ("string_buffer", ctypes.c_char * 1024),
        ("string_offset", ctypes.c_size_t),
    ]

# String packing with little-endian order
def packed_string(s):
    data = s.encode('utf-8')
    alignment = 8  # Align to 8 bytes
    padding_size = (alignment - (len(data) % alignment)) % alignment
    aligned_data = data + b'\x00' * padding_size
    return [
        int.from_bytes(aligned_data[i:i + 8], byteorder='little', signed=True)
        for i in range(0, len(aligned_data), 8)
    ]

# Test bytecode
byte_code = [
    0x1111000000000002, 2,  # type_string, packed_len
    *packed_string("hello world"),  # Packed string data
    0xCCCC000000000001, 1, 1,  # type_command, id_puts, num_args
    0x1111000000000001, 640,  # type_number
    0x1111000000000001, 480,  # type_number
    0xCCCC000000000001, 12, 2,  # type_command, id_open_window, num_args
    0xCCCC000000000001, 0, 0,  # type_command, id_return, 0 args
]

# Initialize stack
stack = Stack()
vm.init_stack(ctypes.byref(stack))

# Convert Python list to ctypes array
byte_code_array = (ctypes.c_int64 * len(byte_code))(*byte_code)

# Execute bytecode
vm.execute_bytecode(ctypes.byref(stack), byte_code_array, len(byte_code))
