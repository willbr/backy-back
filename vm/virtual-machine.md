### Bytecode Encoding Summary

The bytecode is a structured sequence of integers representing operations and data for the virtual machine (VM). It is encoded as follows:

1. **Data Types**:
   - **Numbers**: `[type_number, value]`
     - `type_number` is a unique identifier for numeric values.
     - `value` is the integer to be pushed onto the stack.
   - **Strings**: `[type_string, length, packed_data...]`
     - `type_string` identifies a string.
     - `length` is the number of 64-bit words in the packed string.
     - `packed_data` contains the UTF-8 encoded string, padded to 64-bit alignment.

2. **Commands**:
   - `[type_command, command_id]`
     - `type_command` marks a command.
     - `command_id` specifies the operation (e.g., `id_puts`, `id_open_window`).

### Example Encoding
- Push `"hello world"`:  
  `[type_string, 2, packed_word1, packed_word2]`
  - The string is UTF-8 encoded and padded to two 64-bit words.
- Push `640`:  
  `[type_number, 640]`
- Execute `puts`:  
  `[type_command, id_puts, 1]`

The VM decodes these instructions sequentially, reconstructing strings or processing commands based on the encoded type and accompanying data.
