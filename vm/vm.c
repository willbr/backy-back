
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STACK_SIZE 1024
#define STRING_BUFFER_SIZE 1024

#define TYPE_NUMBER 0x1111000000000001
#define TYPE_STRING 0x1111000000000002
#define TYPE_COMMAND 0xCCCC000000000001

#define ID_RETURN 0
#define ID_PUTS 1
#define ID_OPEN_WINDOW 12

typedef struct {
    int64_t stack[STACK_SIZE];
    int64_t *top;
    int64_t *end;
    char string_buffer[STRING_BUFFER_SIZE];
    size_t string_offset;
} Stack;

__declspec(dllexport) void init_stack(Stack *stack) {
    stack->top = stack->stack;
    stack->end = stack->stack + STACK_SIZE;
    stack->string_offset = 0;
}

__declspec(dllexport) void push_number(Stack *stack, int64_t value) {
    if (stack->top + 2 > stack->end) {
        fprintf(stderr, "Stack overflow: Not enough space to push number.\n");
        exit(EXIT_FAILURE);
    }
    *stack->top++ = value;
    *stack->top++ = TYPE_NUMBER;
}

__declspec(dllexport) int64_t pop_number(Stack *stack) {
    if (stack->top - 2 < stack->stack) {
        fprintf(stderr, "Stack underflow: No numbers to pop.\n");
        exit(EXIT_FAILURE);
    }
    if (*--stack->top != TYPE_NUMBER) {
        fprintf(stderr, "Type error: Expected number type.\n");
        exit(EXIT_FAILURE);
    }
    return *--stack->top;
}

__declspec(dllexport) void push_string(Stack *stack, const char *string) {
    size_t len = strlen(string);
    size_t aligned_len = (len + 7) & ~7;

    if (stack->string_offset + aligned_len > STRING_BUFFER_SIZE) {
        fprintf(stderr, "String buffer overflow: Not enough space to push string.\n");
        exit(EXIT_FAILURE);
    }

    char *dest = stack->string_buffer + stack->string_offset;
    memcpy(dest, string, len);
    memset(dest + len, 0, aligned_len - len);

    size_t offset = stack->string_offset;
    stack->string_offset += aligned_len;

    if (stack->top + 3 > stack->end) {
        fprintf(stderr, "Stack overflow: Not enough space to push string metadata.\n");
        exit(EXIT_FAILURE);
    }
    *stack->top++ = offset;
    *stack->top++ = len;
    *stack->top++ = TYPE_STRING;
}

__declspec(dllexport) const char *pop_string(Stack *stack) {
    if (stack->top - 3 < stack->stack) {
        fprintf(stderr, "Stack underflow: No strings to pop.\n");
        exit(EXIT_FAILURE);
    }
    if (*--stack->top != TYPE_STRING) {
        fprintf(stderr, "Type error: Expected string type.\n");
        exit(EXIT_FAILURE);
    }
    size_t len = *--stack->top;
    size_t offset = *--stack->top;

    if (offset + len > STRING_BUFFER_SIZE) {
        fprintf(stderr, "String buffer corruption detected.\n");
        exit(EXIT_FAILURE);
    }
    return stack->string_buffer + offset;
}

__declspec(dllexport) void execute_bytecode(Stack *stack, const int64_t *bytecode, size_t bytecode_len) {
    size_t i = 0;

    while (i < bytecode_len) {
        int64_t op = bytecode[i++];

        if (op == TYPE_NUMBER) {
            int64_t value = bytecode[i++];
            push_number(stack, value);
        } else if (op == TYPE_STRING) {
            size_t packed_len = bytecode[i++];
            char buffer[256] = {0};
            for (size_t j = 0; j < packed_len; ++j) {
                int64_t chunk = bytecode[i++];
                memcpy(buffer + j * 8, &chunk, 8);
            }
            push_string(stack, buffer);
        } else if (op == TYPE_COMMAND) {
            int64_t cmd_id = bytecode[i++];
            int64_t num_args = bytecode[i++];

            if (cmd_id == ID_RETURN) {
                printf("Return command executed.\n");
                break;
            } else if (cmd_id == ID_PUTS) {
                const char *s = pop_string(stack);
                printf("%s\n", s);
            } else if (cmd_id == ID_OPEN_WINDOW) {
                int64_t height = pop_number(stack);
                int64_t width = pop_number(stack);
                printf("Open window: width=%lld, height=%lld\n", width, height);
            } else {
                fprintf(stderr, "Unknown command: %lld\n", cmd_id);
                exit(EXIT_FAILURE);
            }
        } else {
            fprintf(stderr, "Unknown operation: %lld\n", op);
            exit(EXIT_FAILURE);
        }
    }
}

