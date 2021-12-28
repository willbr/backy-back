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

int echo_newlines = 1;
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

int state_index = 0;
void (*state_fns[16])(void);

char* next_word(void);

#define LIST_OF_STATES \
    X(prefix_head) \
    X(prefix_body) \
    X(prefix_newline) \
    X(prefix_indent) \
    X(prefix_end)

#define X(s) \
    void s(void);
LIST_OF_STATES
#undef X


void
debug_stack(void)
{
    int i = 0;

    if (state_index < 0)
        die("cmd stack underflow");

    /*fprintf(stderr, "%s", line_buffer);*/
    /*debug_var("p", in);*/
    /*debug_var("zu", in - line_buffer);*/
    /*debug_var("s", line_buffer);*/
    /*debug_var("s", token_buffer);*/


    fprintf(stderr, "\nstack:\n");
    for (i = 0; i <= state_index; i += 1) {
        char *fn = NULL;

        if (state_fns[i] == NULL) {
            fn = "(null)";

#define X(s) \
    } else if (state_fns[i] == s) { \
        fn = #s;

        LIST_OF_STATES
        } else {
            debug_var("p", state_fns[i]);
            die("other");
        }
#undef X
        fprintf(stderr, "    %d, %s\n", i, fn);
    }
    fprintf(stderr, "\n");
}


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
    /*ere;*/
    char *r = fgets(line_buffer, 256, f);
    if (r == NULL)
        line_buffer[0] = '\0';
    in = &line_buffer[0];
    /*ere;*/
    /*fprintf(stderr, "line:\n%s\n", line_buffer);*/
    return r;
}


void
read_token(void)
{
    char *tok;
    int tok_len = 0;

    if (*in == '\0')
        if (!read_line())
            return;

    tok = in;

    while (!strchr(token_breakchars, *in))
        in += 1;

    tok_len = in - tok;

    /*ere;*/
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
peek_token(void)
{
    char *old = in;
    read_token();
    in = old;
}


void
parse_indent(void)
{
    /*ere;*/
    char *first_char = NULL;
    uint diff = 0;

    if (*in == '\0')
        read_line();

    while(*in == '\n')
        if (read_line() == NULL) {
            new_indent = 0;
            return;
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
prefix_body(void)
{
    /*ere;*/

    if (*in == '\0') {
        /* EOF */
        prefix_newline();
        return;
    }

    if (*in == ' ')
        die("space")

    if (*in == '\n') {
        state_fns[state_index] = prefix_newline;
        prefix_newline();
        return;
    }

    read_token();
}


void
prefix_newline(void)
{
    /*ere;*/
    if (*in == '\0') {
        strncpy(token_buffer, "", 256);
        return;
    }

    if (*in != '\n') {
        /*debug_var("d", *in);*/
        die("opps");
    }

    /*ere;*/
    in += 1;

    state_fns[state_index] = prefix_indent;

    if (echo_newlines)
        strncpy(token_buffer, "newline", 256);
    else
        prefix_indent();

    return;
}


void
prefix_indent(void)
{
    /*ere;*/
    /*debug_var("d", cur_indent);*/

    parse_indent();
    int diff = new_indent - cur_indent;
    /*ere;*/
    /*debug_var("d", new_indent);*/
    /*debug_var("d", diff);*/

    peek_token();

    if (!strcmp("\\", token_buffer)) {
        if (diff > 1) {
            die(">1");
        } else if (diff == 1) {
            new_indent = cur_indent;
            read_token();
            state_fns[state_index] = prefix_body;
            prefix_body();
            return;
        } else if (diff == 0) {
            die("0");
        } else {
            debug_var("d", diff);
            die("?");
        }
    }

    if (diff > 1) {
        die(">1");
    } else if (diff == 1) {
        cur_indent = new_indent;
        state_fns[state_index] = prefix_end;
        state_index += 1;
        state_fns[state_index] = prefix_head;
        prefix_head();
        return;
    }

    state_fns[state_index] = prefix_end;
    prefix_end();
}


void
prefix_end(void)
{
    /*ere;*/
    /*debug_var("d", cur_indent);*/
    /*debug_var("d", new_indent);*/
    /*debug_stack();*/

    strncpy(token_buffer, "]", 256);

    if (new_indent == cur_indent) {
        state_fns[state_index] = prefix_head;
    } else if (new_indent < cur_indent) {
        cur_indent  -= 1;
        state_index -= 1;
    } else {
        die("opps");
    }

    return;
}


void
prefix_head(void)
{
    /*ere;*/
    /*debug_var("d", *in);*/
    peek_token();

    if (*in == '\0') {
        /*ere;*/
        /*debug_var("d", cur_indent);*/
        /*debug_var("d", new_indent);*/

        if(cur_indent) {
            new_indent = 0;
            state_fns[state_index] = prefix_end;
            prefix_end();
            return;
        }

        token_buffer[0] = '\0';
        return;
    }

    strncpy(token_buffer, "[", 256);
    state_fns[state_index] = prefix_body;
}


char *
next_word(void)
{
    void_fn *fn;

    /*ere;*/
    /*debug_stack();*/

    if (next_token_buffer[0] != '\0') {
        /*ere;*/
        strncpy(token_buffer, next_token_buffer, 256);
        next_token_buffer[0] = '\0';
        return;
    }

    if (state_index < 0) {
        /*ere;*/
        debug_stack();
        die("state underflow");
    }
    /*ere;*/

    if ((fn = state_fns[state_index]) == NULL)
        die("fn is NULL");

    fn();
    return token_buffer;
}


void
init(void)
{
    in = line_buffer;

    state_index = 0;
    state_fns[state_index] = prefix_head;
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

    int limit = 0xff;
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

    if (state_index) {
        debug_stack();
        die("ere");
    }

    fclose(f);

    /*puts("bye");*/
    return 0;
}

