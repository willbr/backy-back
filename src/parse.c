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

typedef unsigned int uint;
typedef void (void_fn)(void);

uint cur_indent = 0;
uint indent_width = 4;
char line_buffer[256] = "";
char *in = NULL;
FILE *f = NULL;
char *tok = NULL;
uint tok_len = 0;

int prefix_index = 0;
char prefix_chars[64] = "";
void (*prefix_fns[64])(void);

char *prefix_breakchars = " ,()[]{}\n";

char *cmds[16];
int depth = 0;
void (*state_fns[16])(void);

int wrapped_index = 0;
char *wrapped[64];

void_fn * lookup_prefix(char c);

void parse_prefix_body(void);
void parse_prefix_head(void); 

void parse_inline_prefix(void);
void parse_inline_prefix_body(void);
void parse_inline_prefix_end(void);

void parse_inline_infix(void);
void parse_inline_infix_arg(void);
void parse_inline_infix_first_op(void);
void parse_inline_infix_op(void);
void parse_inline_infix_end(void);

void parse_inline_postfix(void);
void parse_inline_postfix_body(void);
void parse_inline_postfix_end(void);

void next_word(void);

#define LIST_OF_STATES \
    X(parse_prefix_head) \
    X(parse_prefix_body) \
    X(parse_inline_prefix) \
    X(parse_inline_prefix_body) \
    X(parse_inline_prefix_end) \
    X(parse_inline_infix) \
    X(parse_inline_infix_arg) \
    X(parse_inline_infix_first_op) \
    X(parse_inline_infix_op) \
    X(parse_inline_infix_end) \
    X(parse_inline_postfix) \
    X(parse_inline_postfix_body) \
    X(parse_inline_postfix_end)

void
debug_stack(void)
{
    int i = 0;

    if (depth < 0)
        die("cmd stack underflow");

    fprintf(stderr, "\nstack:\n");
    for (i = 0; i <= depth; i += 1) {
        char *fn = NULL;
#define X(s) \
    } else if (state_fns[i] == s) { \
        fn = #s;
        if (state_fns[i] == NULL) {
            fn = "(null)";
            LIST_OF_STATES
        } else {
            debug_var("p", state_fns[i]);
            die("other");
        }
#undef X
        fprintf(stderr, "    %d, %s, %s\n", i, fn, cmds[i]);
    }
    fprintf(stderr, "\n");
}


void
debug_token(void)
{
    fprintf(stderr, "tok: %d, '%.*s'\n", tok_len, tok_len, tok);
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
    /*ere;*/
    /*debug_var("d", *in);*/
    tok = in;
    while (!strchr(prefix_breakchars, *in))
        in += 1;
    tok_len = in - tok;
    chomp(' ');
}


void
peek_token(void)
{
    char *old = in;
    read_token();
    in = old;
}


int
parse_indent(int *indent)
{
    char *first_char = NULL;
    uint diff = 0;

    while(*in == '\n')
        if (read_line() == NULL)
            return -1;

    first_char = in;
    chomp(' ');

    diff = in - first_char;
    if (diff % indent_width != 0)
        die("invalid indent");

    *indent = diff / indent_width;
    return 0;
}


void
parse_prefix_body(void)
{
    /*ere;*/
    static int diff = 0;
    void (*prefix_fn)(void) = NULL;

    if (diff < 0) {
        /*ere;*/
        tok = cmds[depth];
        tok_len = strlen(tok);
        state_fns[depth] = parse_prefix_head;
        diff += 1;
        return;
    }

    /*ere;*/
    /*debug_var("c", *in);*/

    if (*in == '\0')
        die("null char");

    if (*in == ' ')
        die("space")

    if (*in == '\n') {
        int new_indent = 0;
        /*ere;*/

        if (parse_indent(&new_indent)) {
            tok = cmds[depth];
            tok_len = strlen(tok);
            state_fns[depth] = parse_prefix_head;
            return;
        }

        diff = new_indent - cur_indent;

        /*ere;*/
        peek_token();
        /*debug_token();*/

        if (!strncmp("\\", tok, tok_len)) {
            /*ere;*/
            if (diff > 1) {
                die(">1");
            } else if (diff == 1) {
                /*ere;*/
                read_token();
                /*debug_token();*/
                /*ere;*/
                read_token();
                /*debug_token();*/
                return;
            } else if (diff == 0) {
                die("0");
            } else {
                debug_var("d", diff);
                die("?");
            }
        }

        cur_indent = new_indent;
        /*ere;*/
        if (diff > 1) {
            die(">1");
        } else if (diff == 1) {
            depth += 1;
            state_fns[depth] = parse_prefix_head;
            state_fns[depth]();
            return;
        } else if (diff == 0) {
            tok = cmds[depth];
            tok_len = strlen(tok);
            state_fns[depth] = parse_prefix_head;
            return;
        } else {
            /*ere;*/
            tok = cmds[depth];
            tok_len = strlen(tok);
            depth -= 1;
            return;
        }

        die("newline")
    }

    if (prefix_fn = lookup_prefix(*in)) {
        /*ere;*/
        /*debug_var("c", *in);*/
        prefix_fn();
        return;
    }

    read_token();
}


int
is_wrapped(char *s, int len)
{
    int i;

    for (i = 0; i < wrapped_index; i += 1)
        if (!strncmp(wrapped[i], s, len))
            return -1;

    return 0;
}


void
parse_prefix_head(void)
{
    /*ere;*/
    char *cmd  = NULL;
    char *end  = NULL;
    void_fn *prefix_fn = NULL;

    if (*in == '\0' && read_line() == NULL) {
        tok = NULL;
        return;
    }

    if (*in == '\0')
        die("null char")

    if (*in == '\n')
        die("newline")

    if (*in == ' ')
        die("space")

    if (prefix_fn = lookup_prefix(*in)) {
        die("can you start a line with a prefix char?");
        /*prefix_fn();*/
        return;
    }

    read_token();
    /*debug_token();*/

    if (is_wrapped(tok, tok_len)) {
        end = malloc(4 + tok_len + 1);
        if (end == NULL)
            die("malloc failed");
        *end = '\0';
        strncat(end, "end-", 4);
        strncat(end, tok, tok_len);
        /*debug_var("s", end);*/
        cmds[depth] = end;
        state_fns[depth] = parse_prefix_body;
        return;
    }

    cmd = malloc(tok_len + 1);
    if (cmd == NULL)
        die("malloc failed");

    strncpy(cmd, tok, tok_len);
    cmd[tok_len] = '\0';

    cmds[depth] = cmd;
    state_fns[depth] = parse_prefix_body;
    parse_prefix_body();
}


void
parse_inline_prefix_body(void)
{
    void_fn *prefix_fn = NULL;

    /*ere;*/
    /*debug_var("c", *in);*/
    /*debug_stack();*/

    if (*in == '\0')
        die("null char")

    if (*in == '\n')
        die("newline")

    if (*in == ' ')
        die("space")

    if (prefix_fn = lookup_prefix(*in)) {
        /*ere;*/
        prefix_fn();
        return;
    }

    read_token();
    /*debug_token();*/

    return;
}


void
parse_inline_prefix(void)
{
    char *cmd;
    void_fn *prefix_fn = NULL;

    /*ere;*/
    /*debug_var("c", *in);*/

    in += 1;
    chomp(' ');

    /*debug_var("c", *in);*/

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    /*ere;*/
    read_token();
    /*debug_token();*/

    if (is_wrapped(tok, tok_len)) {
        die("wrapped");
    }

    cmd = malloc(tok_len + 1);
    if (cmd == NULL)
        die("malloc failed");

    strncpy(cmd, tok, tok_len);
    cmd[tok_len] = '\0';

    depth += 1;
    cmds[depth] = cmd;
    state_fns[depth] = parse_inline_prefix_body;
    parse_inline_prefix_body();
}


void
parse_inline_prefix_end(void)
{
    in += 1;
    tok = cmds[depth];
    tok_len = strlen(tok);
    depth -= 1;
    return;
}


void
parse_inline_infix(void)
{
    void_fn *prefix_fn = NULL;

    /*ere;*/
    /*debug_var("c", *in);*/

    in += 1;
    chomp(' ');

    /*debug_var("c", *in);*/

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    /*ere;*/
    read_token();
    /*debug_token();*/

    if (is_wrapped(tok, tok_len)) {
        die("wrapped");
    }

    depth += 1;
    cmds[depth] = NULL;
    state_fns[depth] = parse_inline_infix_first_op;
    /*debug_stack();*/
    /*debug_token();*/
}


void
parse_inline_infix_first_op(void)
{
    char *cmd = NULL;
    void_fn *prefix_fn = NULL;

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    /*ere;*/
    read_token();
    /*debug_token();*/

    cmd = malloc(tok_len + 1);
    if (cmd == NULL)
        die("malloc failed");

    strncpy(cmd, tok, tok_len);
    cmd[tok_len] = '\0';

    cmds[depth] = cmd;
    state_fns[depth] = parse_inline_infix_arg;
    next_word();
}


void
parse_inline_infix_op(void)
{
    void_fn *prefix_fn = NULL;

    /*ere;*/
    /*debug_stack();*/

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    peek_token();

    if (!strncmp(cmds[depth], tok, tok_len)) {
        read_token();
    } else {
        debug_var("s", cmds[depth]);
        debug_token();
        die("different");
    }

    /*tok = cmds[depth];*/
    /*tok_len = strlen(tok);*/
    state_fns[depth] = parse_inline_infix_arg;
    /*die("adsf");*/
}


void
parse_inline_infix_arg(void)
{
    void_fn *prefix_fn = NULL;

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    read_token();
    state_fns[depth] = parse_inline_infix_op;
}


void
parse_inline_infix_end(void)
{
    /*ere;*/
    /*debug_stack();*/

    in += 1;
    chomp(' ');
    tok = cmds[depth];
    depth -= 1;

    if (tok == NULL) {
        next_word();
    } else {
        tok_len = strlen(tok);
    }
}


void
parse_inline_postfix(void)
{
    in += 1;
    chomp(' ');
    depth += 1;
    state_fns[depth] = parse_inline_postfix_body;
    next_word();
}


void
parse_inline_postfix_body(void)
{
    /*ere;*/
    void_fn *prefix_fn = NULL;

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    read_token();
}


void
parse_inline_postfix_end(void)
{
    in += 1;
    chomp(' ');
    depth -= 1;
    next_word();
}


void
define_wrap(char *s)
{
    int max_size = sizeof(wrapped) / sizeof(wrapped[0]);

    if (wrapped_index >= max_size)
        die("wrapped overflow");

    wrapped[wrapped_index] = s;
    wrapped_index += 1;
}


void_fn *
lookup_prefix(char c)
{
    int i;
    for (i = 0; i < prefix_index; i += 1)
        if (c == prefix_chars[i])
            return prefix_fns[i];
    return NULL;
}


void
define_prefix(char c, void (*fn)(void))
{
    int max_size = sizeof(prefix_chars);

    if (prefix_index >= max_size)
        die("prefix overflow");

    prefix_chars[prefix_index] = c;
    prefix_fns[prefix_index]   = fn;
    prefix_index += 1;
}


void
next_word(void)
{
    /*ere;*/
    /*debug_var("d", depth);*/
    /*debug_stack();*/
    if (depth < 0)
        die("state underflow");
    state_fns[depth]();
}


int
main(int argc, char **argv)
{
    memset(wrapped, 0, sizeof(wrapped));

    define_wrap(":");

    define_prefix('[', parse_inline_prefix);
    define_prefix(']', parse_inline_prefix_end);
    define_prefix('(', parse_inline_infix);
    define_prefix(')', parse_inline_infix_end);
    define_prefix('{', parse_inline_postfix);
    define_prefix('}', parse_inline_postfix_end);

    if ((f = fopen(".\\src\\examples\\tokens12.ie", "r")) == NULL)
        die("failed to open file");

    read_line();

    depth = 0;
    state_fns[depth] = parse_prefix_head;

    int i = 10;
    while (next_word(), tok && tok_len) {
        /*ere;*/
        /*debug_stack();*/
        printf("token '%.*s'\n", tok_len, tok);
        if (!i--) {
            debug_var("c", *in);
            die("limit");
        }
    }

    if (*in)
        debug_var("c", *in);
    /*ere;*/

    while (depth) {
        ere;
        printf("token %s\n", cmds[depth]);
        depth -= 1;
    }

    fclose(f);

    puts("bye");
    return 0;
}

