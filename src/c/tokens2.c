#include <stdio.h> /* puts, fopen, fprintf */
#include <stdlib.h> /* exit */
#include <string.h> /* strncmp */

#define ESC "\x1b"
#define RED_TEXT "31"
#define YELLOW_TEXT "33"
#define RESET ESC "[0m"

#define CTEXT(c, s) ESC "[" c "m" s RESET

#define ere \
    do { \
        fprintf(stderr, \
                CTEXT(YELLOW_TEXT, "\n%s : %d : %s\n"), \
                __FILE__, __LINE__, __func__); \
    } while (0);

#define die(msg, ...) \
    do { \
        fprintf(stderr, \
                CTEXT(RED_TEXT, "\nerror: " msg "\n"), \
                ## __VA_ARGS__); \
        ere; \
        exit(1); \
    } while (0);

#define debug_var(s,v) \
    fprintf(stderr, #v ": %" s "\n", v)

typedef unsigned char u8;
typedef unsigned int uint;
typedef void (void_fn)(void);

int echo_indents = 0;
int cur_indent = 0;
int new_indent = 0;
uint indent_width = 4;

char *in = NULL;
char line_buffer[256] = "";

char token_buffer[256] = "";
char next_token_buffer[256] = "";

FILE *f = NULL;

char *token_breakchars = " ,()[]{}\n";

void next_word(void);

#define LIST_OF_STATES \
    X(prefix_head) \
    X(prefix_body) \
    X(prefix_indent) \
    X(prefix_end)

typedef enum token_states {
#define X(s) \
    s,
    LIST_OF_STATES
#undef X

} token_states;

token_states state = 0;



void
debug_token(void)
{
    fprintf(stderr, "tok: %d, '%s'\n", strlen(token_buffer), token_buffer);
}


void
chomp(char c)
{
    while (*in == c)
        in += 1;
}


char *
read_line(void)
{
    char *r = fgets(line_buffer, 256, f);
    if (r == NULL)
        line_buffer[0] = '\0';
    in = &line_buffer[0];
    return r;
}


void
read_token(void)
{
    char *tok;
    int tok_len = 0;

    tok = in;

    while (!strchr(token_breakchars, *in))
        in += 1;

    tok_len = in - tok;

    if (tok_len == 0) {
        if (*in == ' ')
            die("what?");
        in += 1;
        tok_len = 1;
    }

    chomp(' ');

    if (tok_len) {
        strncpy(token_buffer, tok, tok_len);
        token_buffer[tok_len] = '\0';
    } else {
        token_buffer[0] = '\0';
    }
}


void
read_string(void)
{
    char *tok;
    int tok_len = 0;

    tok = in;

    for (;*in != '\0';in += 1) {
    }

    tok_len = in - tok;

    if (tok_len == 0) {
        if (*in == ' ')
            die("what?");
        in += 1;
        tok_len = 1;
    }

    chomp(' ');

    if (tok_len) {
        strncpy(token_buffer, tok, tok_len);
        token_buffer[tok_len] = '\0';
    } else {
        token_buffer[0] = '\0';
    }
}


void
parse_indent(void)
{
    char *first_char = NULL;
    uint diff = 0;

    if (*in == '\0')
        read_line();

    while(*in == '\n') {
        if (read_line() == NULL) {
            new_indent = 0;
            return;
        }
    }

    first_char = in;
    chomp(' ');

    diff = in - first_char;
    /*ere;*/
    /*debug_var("d", diff);*/
    if (diff % indent_width != 0)
        die("invalid indent");

    new_indent = diff / indent_width;
    return;
}


void
read_indent()
{
    parse_indent();
    int diff = new_indent - cur_indent;

    /*ere;*/
    /*debug_var("d", diff);*/

    if (diff == 1) {
        strncpy(token_buffer, "ie/indent", 256);
        state = prefix_head;
    } else {
        die("??");
    }
}


void
next_word(void)
{
    if (*in == '\0') {
        if (!read_line()) {
            token_buffer[0] = '\0';
            return;
        }
    }

    switch (state) {
    case prefix_indent:
        if (*in == ' ') {
            read_indent();
            break;
        }
        die("ere");
        break;

    case prefix_head:
        switch (*in) {
        case '\0':
            die("null");

        case '"':
            read_string();
            break;

        default:
            read_token();
            if (!strcmp("\n", token_buffer)) {
                strncpy(token_buffer, "ie/newline", 256);
                state = prefix_indent;
            }
        }
        break;


    default:
        die("default");
    }
}


void
init(void)
{
    in = line_buffer;
    state = prefix_head;
}


int
main(int argc, char **argv)
{
    char **arg = argv + 1;

    if (!*arg)
        die("missing input filename");

    if (!strcmp(*arg, "-")) {
        /*puts("stdin");*/
        f = stdin;
    } else {
        if ((f = fopen(*arg, "r")) == NULL)
            die("failed to open file");
    }

    init();

    int limit = 0xf;
    while (next_word(), token_buffer[0] != '\0') {
        if (echo_indents)
            for (int i = cur_indent; i; i -= 1)
                fprintf(stderr, "    ");

        /*printf(CTEXT(RED_TEXT, "%s\n"), token_buffer);*/
        printf("%s\n", token_buffer);

        if (!limit--) {
            ere;
            debug_var("d", *in);
            debug_var("c", *in);
            die("limit");
        }
    }

    /*printf("\n");*/

    if (*in)
        debug_var("c", *in);

    fclose(f);

    /*puts("bye");*/
    return 0;
}

