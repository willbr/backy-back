import ctypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000

PAGE_READONLY          = 0x02
PAGE_READWRITE         = 0x04
PAGE_EXECUTE_READ      = 0x20
PAGE_EXECUTE_READWRITE = 0x40

VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.restype = ctypes.c_void_p
VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.c_uint]

VirtualFree = kernel32.VirtualFree
VirtualFree.restype = ctypes.c_int
VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint]

VirtualProtect = kernel32.VirtualProtect
VirtualProtect.restype = ctypes.c_int
VirtualProtect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint)]

def execute(machine_code):
    try:
        # Allocate executable memory
        writable_address = VirtualAlloc(
                None,
                len(machine_code),
                MEM_COMMIT | MEM_RESERVE,
                PAGE_EXECUTE_READWRITE)

        print(f"Writing to memory at: {hex(writable_address)}")
        ctypes.memmove(writable_address, machine_code, len(machine_code))

        # Cast the memory to a callable function
        func_type = ctypes.CFUNCTYPE(None)
        func_ptr = func_type(writable_address)

        # Execute the machine code
        print("Executing machine code...")
        func_ptr()
        print("Machine code executed successfully.")

        # Free the memory
        VirtualFree(
            writable_address, 0, 0x8000  # MEM_RELEASE
        )

    except OSError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Minimal machine code: "ret" instruction
    machine_code = b"\xC3"  # ret
    execute(machine_code)

