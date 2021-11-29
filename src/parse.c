#include <stdio.h> /* puts, fopen, fprintf */
#include <stdlib.h> /* exit */

#define ere \
    do { \
        fprintf(stderr, "\n%s : %d : %s\n", __FILE__, __LINE__, __func__); \
    } while (0);

#define die(msg) \
    do { \
        fprintf(stderr, "\nerror: " msg "\n"); \
        ere; \
        exit(1); \
    } while (0);

typedef unsigned int uint;


uint cur_indent = 0;
uint indent_width = 4;
char *break_chars = " ,()[]{}\n";
char line_buffer[256] = "";
char token_buffer[256] = "";
char *c = NULL;
FILE *f = NULL;
uint i = 0;
char *tok = NULL;
uint tok_len = 0;


struct parser {
    void (*chomp)();
    void (*parse_token)();
};

typedef struct parser parser;


void
chomp(void)
{
    while (*c == ' ')
        c += 1;
}


char *
read_line(void)
{
    char *r = fgets(line_buffer, 256, f);
    if (r == NULL)
        line_buffer[0] = '\0';
    c = &line_buffer[0];
    return r;
}


int
str_contains(char *s, char c)
{
    while (*s != '\0') {
        if (*s == c)
            return 1;
        s += 1;
    }

    return 0;
}


uint
str_ncmp(char *s1, char *s2, uint n)
{
    while (n && *s1 != '\0' && *s2 != '\0') {
        if (*s1 < *s2)
            return -1;
        else if (*s2 < *s1)
            return 1;
        s1 += 1;
        s2 += 1;
        n -= 1;
    }
    return 0;
}


void
parse_token(char *buf, uint *i)
{
    tok = c;
    while (!str_contains(break_chars, *c))
        c += 1;
    tok_len = c - tok;
}


uint
parse_newline(parser *p)
{
    char *first_char = NULL;
    uint indent = 0;
    uint diff = 0;

    while(*c == '\n')
        read_line();

    first_char = c;
    chomp();

    diff = c - first_char;
    if (diff % indent_width != 0)
        die("invalid indent");

    indent = diff / indent_width;
    return indent;
}


void
next_word(parser *p)
{
    uint new_indent = 0;
    uint diff       = 0;

    p->chomp();

    if (*c == '\0') {
        tok = NULL;
        return;
    } else if (*c == '\n') {
        new_indent = parse_newline(p);
        diff = new_indent - cur_indent;

        p->parse_token();

        if (!str_ncmp("\\", tok, tok_len)) {
            if (diff == 1) {
                c += 1;
                p->chomp();
                p->parse_token();
            } else {
                die("line continuation2");
            }
        } else {
            printf("c %d\n", *c);
            printf("tok %.*s\n", tok_len, tok);
            die("newline");
        }

        return;
    }

    p->parse_token();
}


int
main(int argc, char **argv)
{
    parser pp = {};
    parser *p = &pp;

    p->chomp = chomp;
    p->parse_token = parse_token;

    if ((f = fopen(".\\src\\examples\\tokens1.ie", "r")) == NULL)
        die("failed to open file");

    read_line();

    while (next_word(p), tok) {
        printf("tok: %d: '%.*s'\n", tok_len, tok_len, tok);
    }

    fclose(f);

    puts("bye");
    return 0;
}

