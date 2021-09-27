#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int indent_width = 2;

enum bools {
    false = 0,
    true  = 1
};

enum states {
    unknown,
    reading_token,
    reading_newline
};


int read_token(char *token, int token_length, char **buffer);
int read_indent(int *new_indent, char **buffer);
void die(const char * const msg);


int
main(int argc, char **argv)
{
    char buffer[1024] = "";
    char token[256]   = "";
    char *s           = NULL;

    int error      = 0;
    int indent     = 0;
    int new_indent = 0;
    int delta      = 0;

    enum states state = reading_token;

    while (fgets(buffer, sizeof(buffer), stdin)) {
        /*printf("buffer: %s", buffer);*/
        s = buffer;
        while (*s != '\0') {
            switch (*s) {
            case ' ':
                if (state == reading_token)
                    die("error: unexpected space");

                if ((error = read_indent(&new_indent, &s)))
                    die("error");

                delta =  new_indent - indent;

                if (delta < 0) {
                    while (delta++ < 0)
                        puts("dedent");

                } else if (delta == 0) {
                    puts("newline");

                } else if (delta == 1) {
                    puts("indent");

                } else {
                    fprintf(stderr, "error: invalid indent, old: %d, new: %d\n", indent, new_indent);
                    die("error");
                }

                indent = new_indent;
                state  = reading_token;

                break;

            case '\n':
                s += 1;
                state = reading_newline;
                break;

            default:
                if ((error = read_token(token, sizeof(token), &s)))
                    die("error");

                puts(token);

                while (*s == ' ')
                    s += 1;

            }
        }
    }

    while (indent--)
        puts("dedent");

    return 0;
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

    strncpy(token, s, len);
    *(token + len) = '\0';

    *buffer = end;

    return 0;
}


int
read_indent(int *new_indent, char **buffer)
{
    char *s   = *buffer;
    char *end = NULL;
    int   len = 0;

    end = s;
    while (*end == ' ')
        end += 1;

    len = end - s;

    if ((len % indent_width) != 0) {
        fprintf(stderr, "error invalid indent width: %d\n", len);
        return 1;
    }

    *new_indent = len / indent_width;

    /* match line continuation */
    if (*end == '\\') {
        switch (*(s + 1)) {
        case '\0':
            die("error; EOF following line continuation");
            break;

        case '\t':
            die("error; tab following line continuation");
            break;

        case '\n':
            die("error; newline following line continuation");
            break;

        case ' ':
            end += 2;
            new_indent -= 1;
            break;
        }
    }

    *buffer = end;
    return 0;
}


void
die(const char * const msg)
{
    fprintf(stderr, "%s\n", msg);
    exit(1);
}

