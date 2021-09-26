#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int indent_width = 2;

int read_token(char *token, int token_length, char **buffer);
int read_indent(int *new_indent, char **buffer);

int
main(int argc, char **argv)
{
    char token[256] = "";
    char *code =
        "+ 1 2\n"
        "  + 3 4\n"
        "    + 5 6";
    char *s    = code;
    int error      = 0;
    int indent     = 0;
    int new_indent = 0;

    while (*s != '\0') {
        switch (*s) {
        case ' ':
            printf("%s\n", s);
            fprintf(stderr, "error: unexpected space\n");
            goto errhandle;
            break;

        case '\n':
            if (error = read_indent(&new_indent, &s))
                goto errhandle;
            switch (new_indent - indent) {
            case -1:
                puts("-1");
                break;

            case 0:
                puts("0");
                break;

            case 1:
                puts("indent");
                break;

            default:
                fprintf(stderr, "error: invalid indent, old: %d, new: %d\n", indent, new_indent);
                goto errhandle;
            }
            indent = new_indent;
            break;

        default:
            if (error = read_token(token, sizeof(token), &s))
                goto errhandle;
            while (*s == ' ')
                s += 1;

        }
    }

    while (indent > 0) {
        puts("dedent");
        indent -= 1;
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

    strncpy(token, s, len);

    printf("t: %s\n", token);

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

