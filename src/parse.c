#include <stdio.h> /* puts, fopen, fprintf */
#include <stdlib.h> /* exit */

#define ESC "\x1b"
#define RED_TEXT "31"
#define YELLOW_TEXT "33"
#define RESET ESC "[0m"

#define ere \
    do { \
        fprintf(stderr, \
                ESC "[" YELLOW_TEXT "m" \
                "\n%s : %d : %s\n" \
                RESET, \
                __FILE__, __LINE__, __func__); \
    } while (0);

#define die(msg) \
    do { \
        fprintf(stderr, \
                ESC "[" RED_TEXT "m" \
                "\nerror: " msg "\n" \
                RESET \
                ); \
        ere; \
        exit(1); \
    } while (0);

typedef unsigned int uint;


struct string {
    uint size;
    uint capacity;
    char *cstr;
};
typedef struct string string;

struct parser {
    void (*chomp)();
    void (*parse_token)();
};
typedef struct parser parser;

uint cur_indent = 0;
uint indent_width = 4;
char break_buffer[256] = "";
char line_buffer[256] = "";
char token_buffer[256] = "";
char *c = NULL;
FILE *f = NULL;
uint i = 0;
char *tok = NULL;
uint tok_len = 0;

string token       = {};
string line        = {};
string break_chars = {0, sizeof(break_buffer) - 1, break_buffer};

parser pp = {};
parser *p = &pp;


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
str_contains(string *s, char c)
{
    char *i = s->cstr;

    while (*i != '\0') {
        if (*i == c)
            return 1;
        i += 1;
    }

    return 0;
}


uint
cstr_ncmp(char *s1, char *s2, uint n)
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
    while (!str_contains(&break_chars, *c))
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

        if (!cstr_ncmp("\\", tok, tok_len)) {
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
cstr_len(char *s)
{
    int i = 0;

    if (s == NULL)
        die("s is NULL");

    while (*s++ != '\0')
        i += 1;
    return i;
}


void
str_append_chars(string *s, char *cs)
{
    char *i = cs;
    char *d = s->cstr + s->size;
    int cs_len = cstr_len(cs);
    uint new_size = s->size + cs_len;

    if (new_size > s->capacity)
        die("capacity reached");

    while (*i != '\0')
        *d++ = *i++;
    *d = '\0';

    s->size = new_size;
}

void
init(void)
{
    p->chomp = chomp;
    p->parse_token = parse_token;

    str_append_chars(&break_chars, " ,()[]{}\n");
}


int
main(int argc, char **argv)
{
    init();

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

