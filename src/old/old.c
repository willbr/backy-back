#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int indent_width = 2;

struct cmd_stack {
    char  *buffer;
    char  *next;
    char  *end;
    int    count;
    int    limit;
    char *(cmds[16]);
    int    args[16];
};

enum bools {
    false = 0,
    true  = 1
};


int read_token(char *token, int token_length, char **buffer);
int read_indent(int *new_indent, char **buffer);

void  init_cmd_stack(struct cmd_stack *stack, char *buffer, size_t size);
void  print_cmd_stack(struct cmd_stack *stack);
char* push(struct cmd_stack *stack, char *buffer);
char* pop(struct cmd_stack *stack);
char* peek(struct cmd_stack *stack);

int
main(int argc, char **argv)
{
    char *code = NULL;
    char *s    = NULL;
    char *expected_result = NULL;

    char token_data[1024] = "";
    char token[256]       = "";

    char *cmd        = NULL;
    char *parent_cmd = NULL;

    int running    = true;
    int error      = 0;
    int indent     = 0;
    int new_indent = 0;
    int delta      = 0;
    struct cmd_stack stack = {0};

    init_cmd_stack(&stack, token_data, sizeof(token_data));

    switch (6) {
    case 0:
        code = "";
        break;

    case 1:
        code =
            "+ 1 2 3";
        expected_result = "1 2 + 3 +";
        break;

    case 2:
        code =
            "+ 1 2\n"
            "  * 3 4";
        expected_result = "1 2 + 3 4 * +";
        break;

    case 3:
        code =
            "+ 1 2\n"
            "  * 3 4\n"
            "    + 5 6\n";
        expected_result = "1 2 + 3 4 * 5 6 + * +";
        break;

    case 4:
        code =
            "+ 1 2\n"
            "  * 3 4\n"
            "    + 5 6\n"
            "  * 6 6\n"
            "  / 12 2\n";
        expected_result = "1 2 + 3 4 * 5 6 + * + 6 6 * + 12 2 / +";
        break;

    case 5:
        code =
            "double\n"
            "  * 3 4\n";
        expected_result = "3 4 * double";
        break;

    case 6:
        code =
            "+ 3 4 5\n"
            "  + 6 7\n";
        expected_result = "3 4 + 5 + 6 7 + +";
        break;

    default:
        exit(1);
    }

    printf("code:\n%s\n\n", code);
    printf("er:\n%s\n\n", expected_result);
    printf("r:\n");

    s = code;

    while (running) {
        switch (*s) {
        case '\0':
            /*print_cmd_stack(&stack);*/

            while (stack.count) {
                cmd = pop(&stack);
                printf("%s ", cmd);
            }

            printf("\n");

            running = false;
            break;

        case ' ':
            fprintf(stderr, "error: unexpected space\n");
            goto errhandle;
            break;

        case '\n':
            if ((error = read_indent(&new_indent, &s)))
                goto errhandle;

            delta =  new_indent - indent;

            if (delta < 0) {
                /*printf("dedent ");*/
                for (; delta < 0; delta += 1) {
                    parent_cmd = pop(&stack);
                    printf("%s ", parent_cmd);
                }

            } else if (delta == 0) {
                cmd = pop(&stack);
                printf("%s ", cmd);

            } else if (delta == 1) {
                int *argsp = &stack.args[stack.count - 1];
                if ((*argsp % 2) == 0) {
                    printf("%s ", cmd);
                }
                /*parent_cmd = peek(&stack);*/
                /*printf("%s ", parent_cmd);*/

            } else {
                fprintf(stderr, "error: invalid indent, old: %d, new: %d\n", indent, new_indent);
                goto errhandle;
            }

            indent = new_indent;
            cmd = NULL;

            break;

        default:
            if ((error = read_token(token, sizeof(token), &s)))
                goto errhandle;

            if (cmd == NULL) {
                cmd = push(&stack, token);
            } else {
                int *argsp = &stack.args[stack.count - 1];
                /*printf("<%d, %d> ", *argsp, *argsp % 2);*/
                if ((*argsp > 0) && ((*argsp % 2) == 0)) {
                    printf("%s ", cmd);
                }
                printf("%s ", token);
                *argsp += 1;
            }


            while (*s == ' ')
                s += 1;

        }
    }


    return 0;

errhandle:
    /*fprintf(stderr, "exit with error\n");*/
    return 1;
}


int
read_token(char *token, int token_length, char **buffer)
{
    int   len = 0;
    char *end = NULL;
    char *s   = *buffer;

    end = s;

    while (*end != ' ' && *end != '\n' && *end != '\0')
        end += 1;

    len = end - s;

    if (len == 0) {
        fprintf(stderr, "no more tokens\n");
        return 1;
    }

    if (len > token_length) {
        fprintf(stderr, "token too long\n");
        return 1;
    }

    /*printf("\ns: %.*s\n", len, s);*/
    strncpy(token, s, len);
    *(token + len) = '\0';

    /*printf("len:%d ", len);*/
    /*printf("t: %s\n", token);*/

    *buffer = end;

    return 0;
}


int
read_indent(int *new_indent, char **buffer)
{
    char *s   = *buffer;
    char *end = NULL;
    int   len = 0;

    s += 1; /* skip newline */

    end = s;
    while (*end == ' ')
        end += 1;

    len = end - s;

    if ((len % indent_width) != 0) {
        fprintf(stderr, "error invalid indent width: %d\n", len);
        return 1;
    }

    *new_indent = len / indent_width;

    *buffer = end;
    return 0;
}


void
init_cmd_stack(struct cmd_stack *stack, char *buffer, size_t size)
{
    stack->buffer    = buffer;
    stack->next      = buffer;
    stack->end       = buffer + size;
    stack->count     = 0;
    stack->limit     = sizeof(stack->cmds) / sizeof(stack->cmds[0]);
    memset(stack->buffer, 0, size);
    memset(stack->args, 0, sizeof(stack->args));
}


char*
push(struct cmd_stack *stack, char *buffer)
{
    int len = strlen(buffer);
    char *rval = stack->next;

    /*printf("push %s\n", buffer);*/

    stack->cmds[stack->count] = stack->next;

    strcpy(stack->next, buffer);
    stack->count += 1;
    stack->next += (len + 1);
    /*print_cmd_stack(stack);*/
    return rval;
}


char*
pop(struct cmd_stack *stack)
{
    if (stack->count == 0)
        return NULL;

    stack->count -= 1;
    stack->next = stack->cmds[stack->count];
    return stack->next;
}


char*
peek(struct cmd_stack *stack)
{
    if (stack->count == 0)
        return NULL;

    return stack->cmds[stack->count - 1];
}


void
print_cmd_stack(struct cmd_stack *stack)
{
    char *s = NULL;
    int   i = 0;

    if (stack == NULL) {
        printf("stack is NULL\n");
        return;
    }

    printf("stack %d:\n", stack->count);

    for (i = 0; i < stack->count; i += 1)
        printf("%d,%s\n", i, stack->cmds[i]);
}


