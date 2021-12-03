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

uint cur_indent = 0;
uint indent_width = 4;

char *in = NULL;
char line_buffer[256] = "";

char token_buffer[256] = "";
int tok_len = 0;

FILE *f = NULL;

int prefix_index = 0;
char prefix_chars[64] = "";
void (*prefix_fns[64])(void);

char *prefix_breakchars = " ,()[]{}\n";

int state_index = 0;
char *cmds[16];
void (*state_fns[16])(void);

int cmds_index = 0;
char cmds_buffer[16 * (256 + 1)] = "";

int wrapped_index = 0;
char *wrapped[64];

void_fn * lookup_prefix(char c);

void prefix_body(void);
void prefix_head(void); 

void inline_prefix(void);
void inline_prefix_body(void);
void inline_prefix_end(void);

void inline_infix(void);
void inline_infix_arg(void);
void inline_infix_first_op(void);
void inline_infix_op(void);
void inline_infix_end(void);

void inline_postfix(void);
void inline_postfix_body(void);
void inline_postfix_end(void);

char* next_word(void);

#define LIST_OF_STATES \
    X(prefix_head) \
    X(prefix_body) \
    X(inline_prefix) \
    X(inline_prefix_body) \
    X(inline_prefix_end) \
    X(inline_infix) \
    X(inline_infix_arg) \
    X(inline_infix_first_op) \
    X(inline_infix_op) \
    X(inline_infix_end) \
    X(inline_postfix) \
    X(inline_postfix_body) \
    X(inline_postfix_end)

void
debug_stack(void)
{
    int i = 0;

    if (state_index < 0)
        die("cmd stack underflow");

    fprintf(stderr, "\nstack:\n");
    for (i = 0; i <= state_index; i += 1) {
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
    fprintf(stderr, "tok: %d, '%s'\n", strlen(token_buffer), token_buffer);
}


void
dump(void *v, int n)
{
    char *c = v;

    fprintf(stderr, "dumping: %d bytes @ %p\n\n", n, v);

    while (n > 0) {
        ptrdiff_t offset = c - v;
        int i = 4;
        int line_length = n > 7 ? 8 : n % 8;

        fprintf(stderr, "%.03zu ", offset);

        for (i = 0; i < 8; i++) {
            char *x = c + i;
            char *gap = i % 2 ? " " : "";
            if (i < line_length)
                fprintf(stderr, "%02x%s", *x, gap);
            else
                fprintf(stderr, "  %s", gap);
        }

        fprintf(stderr, " ");

        for (i = 0; i < 8; i++) {
            char *x = c + i;
            char xx = *x > 10 ? *x : '.';
            char *gap = i % 2 ? " " : "";
            if (i < line_length)
                fprintf(stderr, "%c", xx);
            else
                fprintf(stderr, " ");
        }

        fprintf(stderr, "\n");

        c += 8;
        n -= 8;
    }

    fprintf(stderr, "\n");
}


char *
alloc_cmd(char *s)
{
    char *rval = &cmds_buffer[cmds_index];
    int len = strlen(s);
    int max_size = sizeof(cmds_buffer) / sizeof(cmds_buffer[0]);
    /*debug_var("d", max_size);*/

    if (len > 255)
        die("command string is too long: %d > 255", len);

    /*debug_var("d", cmds_index);*/
    cmds_index += len + 1;
    /*debug_var("d", cmds_index);*/

    if (cmds_index >= max_size)
        die("cmds_buffer overflowed");

    strncpy(rval, s, len+ 1);
    cmds_buffer[cmds_index] = (u8)len;
    cmds_index += 1;
    /*debug_var("d", cmds_index);*/

    /*debug_var("s", rval);*/
    /*dump(cmds_buffer, cmds_index);*/

    /*debug_var("d", len);*/
    return rval;
}


char *
alloc_prefixed_cmd(char *prefix, char* s)
{
    static char prefixed[256] = "";
    int prefix_len = strlen(prefix);
    int s_len = strlen(s);
    int total_len = prefix_len + s_len;

    if (total_len > 255)
        die("prefixed cmd is too long: %d > 255", total_len);

    /*ere;*/
    strncat(prefixed, prefix, 256);
    /*debug_var("s", prefixed);*/
    /*dump(prefixed, 0x20);*/

    strncat(prefixed, s, 256 - prefix_len);
    /*dump(prefixed, 0x20);*/
    /*debug_var("s", prefixed);*/

    return alloc_cmd(prefixed);
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
    char *tok = in;

    while (!strchr(prefix_breakchars, *in))
        in += 1;

    tok_len = in - tok;

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
prefix_body(void)
{
    /*ere;*/
    static int diff = 0;
    void (*prefix_fn)(void) = NULL;

    if (diff < 0) {
        /*ere;*/
        strncpy(token_buffer, cmds[state_index], 256);
        state_fns[state_index] = prefix_head;
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
            strncpy(token_buffer, cmds[state_index], 256);
            state_fns[state_index] = prefix_head;
            return;
        }

        diff = new_indent - cur_indent;

        /*ere;*/
        peek_token();
        /*debug_token();*/

        if (!strcmp("\\", token_buffer)) {
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
            state_index += 1;
            state_fns[state_index] = prefix_head;
            state_fns[state_index]();
            return;
        } else if (diff == 0) {
            strncpy(token_buffer, cmds[state_index], 256);
            state_fns[state_index] = prefix_head;
            return;
        } else {
            /*ere;*/
            strncpy(token_buffer, cmds[state_index], 256);
            state_index -= 1;
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
is_wrapped(char *s)
{
    int i;

    for (i = 0; i < wrapped_index; i += 1)
        if (!strncmp(wrapped[i], s, 256))
            return -1;

    return 0;
}


void
prefix_head(void)
{
    /*ere;*/
    char *end  = NULL;
    void_fn *prefix_fn = NULL;

    if (*in == '\0' && read_line() == NULL) {
        token_buffer[0] = '\0';
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

    if (is_wrapped(token_buffer)) {
        cmds[state_index] = alloc_prefixed_cmd("end-", token_buffer);
        state_fns[state_index] = prefix_body;
        return;
    }


    cmds[state_index] = alloc_cmd(token_buffer);
    state_fns[state_index] = prefix_body;
    next_word();
}


void
inline_prefix_body(void)
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
inline_prefix(void)
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

    if (is_wrapped(token_buffer)) {
        die("wrapped");
    }

    state_index += 1;
    cmds[state_index] = alloc_cmd(token_buffer);
    state_fns[state_index] = inline_prefix_body;
    inline_prefix_body();
}


void
inline_prefix_end(void)
{
    in += 1;
    strncpy(token_buffer, cmds[state_index], 256);
    tok_len = strlen(token_buffer);
    state_index -= 1;
    return;
}


void
inline_infix(void)
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

    if (is_wrapped(token_buffer)) {
        die("wrapped");
    }

    state_index += 1;
    cmds[state_index] = NULL;
    state_fns[state_index] = inline_infix_first_op;
    /*debug_stack();*/
    /*debug_token();*/
}


void
inline_infix_first_op(void)
{
    void_fn *prefix_fn = NULL;

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    /*ere;*/
    read_token();
    /*debug_token();*/

    cmds[state_index] = alloc_cmd(token_buffer);
    state_fns[state_index] = inline_infix_arg;
    next_word();
}


void
inline_infix_op(void)
{
    void_fn *prefix_fn = NULL;

    /*ere;*/
    /*debug_stack();*/

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    peek_token();

    if (!strcmp(cmds[state_index], token_buffer)) {
        read_token();
    } else {
        debug_var("s", cmds[state_index]);
        debug_token();
        die("different");
    }

    /*tok = cmds[state_index];*/
    /*tok_len = strlen(tok);*/
    state_fns[state_index] = inline_infix_arg;
    /*die("adsf");*/
}


void
inline_infix_arg(void)
{
    void_fn *prefix_fn = NULL;

    if (prefix_fn = lookup_prefix(*in)) {
        prefix_fn();
        return;
    }

    read_token();
    state_fns[state_index] = inline_infix_op;
}


void
inline_infix_end(void)
{
    /*ere;*/
    /*debug_stack();*/

    in += 1;
    chomp(' ');
    strncpy(token_buffer, cmds[state_index], 256);
    state_index -= 1;

    if (token_buffer[0] == '\0') {
        next_word();
    } else {
        tok_len = strlen(token_buffer);
    }
}


void
inline_postfix(void)
{
    in += 1;
    chomp(' ');
    state_index += 1;
    state_fns[state_index] = inline_postfix_body;
    next_word();
}


void
inline_postfix_body(void)
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
inline_postfix_end(void)
{
    in += 1;
    chomp(' ');
    state_index -= 1;
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


char *
next_word(void)
{
    /*ere;*/
    /*debug_var("d", state_index);*/
    /*debug_stack();*/
    if (state_index < 0)
        die("state underflow");

    state_fns[state_index]();
    return token_buffer;
}


int
main(int argc, char **argv)
{
    memset(wrapped, 0, sizeof(wrapped));

    define_wrap(":");

    define_prefix('[', inline_prefix);
    define_prefix(']', inline_prefix_end);
    define_prefix('(', inline_infix);
    define_prefix(')', inline_infix_end);
    define_prefix('{', inline_postfix);
    define_prefix('}', inline_postfix_end);

    if ((f = fopen(".\\src\\examples\\tokens0.ie", "r")) == NULL)
        die("failed to open file");

    read_line();

    state_index = 0;
    state_fns[state_index] = prefix_head;

    int i = 60;
    while (next_word(), token_buffer[0] != '\0') {
        /*ere;*/
        /*debug_stack();*/
        printf("token '%s'\n", token_buffer);
        if (!i--) {
            debug_var("c", *in);
            die("limit");
        }
    }
    /*ere;*/

    if (*in)
        debug_var("c", *in);
    /*ere;*/

    /*ere;*/
    while (state_index) {
        /*ere;*/
        printf("token %s\n", cmds[state_index]);
        state_index -= 1;
    }
    /*ere;*/

    fclose(f);

    puts("bye");
    return 0;
}

