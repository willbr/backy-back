#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int read_token(char *token, int token_length, char **buffer);
int read_indent(char **buffer);

int
main(int argc, char **argv)
{
    char token[256] = "";
    char *code = "1 2 +\n3 + ";
    char *s = code;
    int error = 0;

    while (*s != '\0') {
        switch (*s) {
        case '\n':
            error = read_indent(&s);
            break;

        default:
            error = read_token(token, sizeof(token), &s);
        }

        if (error)
            break;
    }

    return 0;
}


int
read_token(char *token, int token_length, char **buffer)
{
    int   len = 0;
    char *end = NULL;
    char *s   = *buffer;

    while (*s == ' ')
        s += 1;

    end = s;

    while (*end != ' ' && *end != '\n' && *end != '\0')
        end += 1;

    len = end - s;
    /*printf("len: %d\n", len);*/

    if (len == 0)
        return 1;

    strncpy(token, s, len);

    printf("t: %s\n", token);

    *buffer = end;

    return 0;
}


int
read_indent(char **buffer)
{
    char *s   = *buffer;
    char *end = NULL;

    s += 1; /* skip newline */

    end = s;
    while (*end == ' ')
        end += 1;

    end = s;
    *buffer = s + 0;
    return 0;
}

