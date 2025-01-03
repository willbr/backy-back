import mmap
import ctypes
import struct
import math


class MachineCodeCompiler:
    def __init__(self):
        self.code = bytearray()
        self.labels = {}  # Dictionary to store label positions
        self.unresolved_jumps = []  # List to store unresolved jump positions

    def emit(self, bytes_):
        """Appends raw bytes to the machine code."""
        self.code.extend(bytes_)

    def label(self, name):
        """Define a label at the current position."""
        if name in self.labels:
            raise ValueError(f"Label '{name}' is already defined")
        self.labels[name] = len(self.code)

    def jump(self, label_name):
        """Emit a jump to a label."""
        # Emit the jump opcode and a placeholder for the offset
        self.emit(b"\xE9")  # Opcode for near jump (jmp rel32)
        placeholder_position = len(self.code)
        self.emit(b"\x00\x00\x00\x00")  # Placeholder for the relative offset
        self.unresolved_jumps.append((placeholder_position, label_name))

    def resolve_labels(self):
        """Resolve label positions and replace placeholders with actual offsets."""
        for position, label_name in self.unresolved_jumps:
            if label_name not in self.labels:
                raise ValueError(f"Undefined label: {label_name}")
            target = self.labels[label_name]
            offset = target - (position + 4)  # Relative offset from next instruction
            self.code[position:position + 4] = struct.pack("<i", offset)

    def mov_rax(self, value):
        """Move an immediate value into RAX."""
        self.emit(b"\x48\xB8")  # Opcode for "mov rax, imm64"
        self.emit(struct.pack("<Q", value))  # 64-bit immediate value

    def call_function(self, address):
        """Call a function at the given address."""
        self.emit(b"\x48\xB8")  # mov rax, imm64
        self.emit(struct.pack("<Q", address))  # Function address
        self.emit(b"\xFF\xD0")  # call rax

    def exit_process(self):
        """Call ExitProcess (Windows)."""
        address = ctypes.windll.kernel32.GetProcAddress(
            ctypes.windll.kernel32.GetModuleHandleA(b"kernel32.dll"), b"ExitProcess"
        )
        self.call_function(address)

    def write_console(self, string_address, length):
        """Call WriteConsoleA (Windows)."""
        address = ctypes.windll.kernel32.GetProcAddress(
            ctypes.windll.kernel32.GetModuleHandleA(b"kernel32.dll"), b"WriteConsoleA"
        )
        # Prepare parameters: (HANDLE, LPVOID, DWORD, LPDWORD, LPVOID)
        self.emit(b"\x48\x31\xC9")  # xor rcx, rcx (HANDLE = stdout, 0)
        self.emit(b"\x48\xBA")      # mov rdx, imm64 (string address)
        self.emit(struct.pack("<Q", string_address))
        self.emit(b"\x48\xBE")      # mov rsi, imm64 (length)
        self.emit(struct.pack("<Q", length))
        self.call_function(address)

    def get_code(self):
        """Return the generated machine code."""
        return bytes(self.code)


def allocate_executable_memory(size):
    """Allocate writable memory and set it as executable on Windows."""
    # Round size up to the next 16-byte boundary for alignment
    aligned_size = math.ceil(size / 16) * 16

    # Allocate writable memory
    memory = mmap.mmap(-1, aligned_size, access=mmap.ACCESS_WRITE)

    # Get the address of the memory buffer
    address = ctypes.addressof(ctypes.c_char.from_buffer(memory))

    print(f"Allocated memory at address: {hex(address)}, size: {aligned_size}")

    # Set the memory to executable
    PAGE_EXECUTE_READWRITE = 0x40
    old_protect = ctypes.c_ulong()
    result = ctypes.windll.kernel32.VirtualProtect(
        ctypes.c_void_p(address), aligned_size, PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect)
    )

    if result == 0:
        # Print detailed error if VirtualProtect fails
        raise ctypes.WinError()

    print("Memory set to executable.")
    return memory

# Example Usage
if __name__ == "__main__":
    # Define a simple machine code to exit
    machine_code = b''
    #machine_code += b"\x48\x31\xC0"  # xor rax, rax
    machine_code += b"\xC3"         # ret

    # Allocate executable memory
    memory = allocate_executable_memory(len(machine_code))

    # Write the machine code into memory
    memory.write(machine_code)

    # Cast the memory to a callable function
    func_type = ctypes.CFUNCTYPE(None)
    func_ptr = func_type(ctypes.addressof(ctypes.c_char.from_buffer(memory)))

    # Execute the machine code
    func_ptr()

    # Free the memory
    memory.close()

