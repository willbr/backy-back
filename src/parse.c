#include <stdio.h> /* puts, fopen, fprintf */
#include <stdlib.h> /* exit */
#include <string.h> /* strncmp */

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

#define debug_var(s,v) \
    fprintf(stderr, #v ": %" s "\n", v)

typedef unsigned int uint;

uint cur_indent = 0;
uint indent_width = 4;
char line_buffer[256] = "";
char *in = NULL;
FILE *f = NULL;
char *tok = NULL;
uint tok_len = 0;

char *prefix_breakchars = " ,()[]{}\n";

char *cmds[16];
uint depth = 0;
void (*state_fn[16])(void);

int wrapped_index = 0;
char *wrapped[64];

void parse_prefix_body(void);
void parse_prefix_head(void); 


void
debug_cmd_stack(void)
{
    int i = 0;
    for (i = 0; i <= depth; i += 1) {
        fprintf(stderr, "cmd: %d, %s\n", i, cmds[i]);
    }
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

    if (diff < 0) {
        /*ere;*/
        tok = cmds[depth];
        tok_len = strlen(tok);
        state_fn[depth] = parse_prefix_head;
        diff += 1;
        return;
    }

    if (*in == '\0')
        die("null char");

    if (*in == '\n') {
        int new_indent = 0;

        if (parse_indent(&new_indent)) {
            tok = cmds[depth];
            tok_len = strlen(tok);
            state_fn[depth] = parse_prefix_head;
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
            state_fn[depth] = parse_prefix_head;
            state_fn[depth]();
            return;
        } else if (diff == 0) {
            die("0");
        } else {
            /*ere;*/
            tok = cmds[depth];
            tok_len = strlen(tok);
            depth -= 1;
            return;
        }

        die("newline")
    }

    if (*in == ' ')
        die("space")

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
        state_fn[depth] = parse_prefix_body;
        return;
    }

    cmd = malloc(tok_len + 1);
    if (cmd == NULL)
        die("malloc failed");

    strncpy(cmd, tok, tok_len);
    cmd[tok_len] = '\0';

    cmds[depth] = cmd;
    state_fn[depth] = parse_prefix_body;
    parse_prefix_body();
}


void
define_wrap(char *s)
{
    int max_size = sizeof(wrapped) / sizeof(wrapped[0]);
    /*debug_var("d", max_size);*/

    if (wrapped_index >= max_size)
        die("wrapped overflow");

    wrapped[wrapped_index++] = s;
}


int
main(int argc, char **argv)
{
    memset(wrapped, 0, sizeof(wrapped));

    define_wrap(":");

    if ((f = fopen(".\\src\\examples\\tokens3.ie", "r")) == NULL)
        die("failed to open file");

    read_line();

    depth = 0;
    state_fn[depth] = parse_prefix_head;

    while (state_fn[depth](), tok) {
        printf("token %.*s\n", tok_len, tok);
    }

    while (depth) {
        ere;
        printf("token %s\n", cmds[depth]);
        depth -= 1;
    }

    fclose(f);

    puts("bye");
    return 0;
}

