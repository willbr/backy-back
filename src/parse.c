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
char tokens_buffer[256] = "";
char *in = NULL;
FILE *f = NULL;
char *tok = NULL;
uint tok_len = 0;

char *prefix_breakchars = " ,()[]{}\n";

char *cmds[16];
uint depth = 0;
void (*(state_fn[16]))(void);


void parse_prefix_body(void);
void parse_prefix_head(void); 

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
    tok = in;
    while (!strchr(prefix_breakchars, *in))
        in += 1;
    tok_len = in - tok;
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
    ere;
    debug_var("d", diff);
    debug_var("d", in);
    debug_var("d", first_char);
    if (diff % indent_width != 0)
        die("invalid indent");

    *indent = diff / indent_width;
    /*fprintf(stderr, "indent: %d\n", indent);*/
    return 0;
}


void
parse_prefix_body(void)
{
    if (*in == '\0')
        die("null char");


    if (*in == '\n') {
        int new_indent = 0;
        int diff       = 0;

        if (parse_indent(&new_indent)) {
            tok = cmds[depth];
            tok_len = strlen(tok);
            state_fn[depth] = parse_prefix_head;
            return;
        }

        ere;
        debug_var("d", cur_indent);
        debug_var("d", new_indent);

        diff = new_indent - cur_indent;
        cur_indent = new_indent;
        debug_var("d", diff);

        die("newline")
    }

    if (*in == ' ')
        die("space")

    read_token();
    chomp(' ');




    /*printf("tok: %.*s\n", tok_len, tok);*/
    /*die("ere");;*/
}

void
parse_prefix_head(void)
{
    if (*in == '\0') {
        if (read_line() == NULL) {
            tok = NULL;
            return;
        }
    }

    if (*in == '\0')
        die("null char")

    if (*in == '\n')
        die("newline")

    if (*in == ' ')
        die("space")

    read_token();
    /*printf("%.*s\n", tok_len, tok);*/

    char *cmd = malloc(tok_len + 1);
    if (cmd == NULL)
        die("malloc failed");
    strncpy(cmd, tok, tok_len);
    /*debug_var("s", cmd);*/
    cmds[depth] = cmd;

    chomp(' ');

    state_fn[depth] = parse_prefix_body;
    parse_prefix_body();

    /*if (*in == '\0') {*/
        /*tok = NULL;*/
        /*return;*/
    /*} else if (*in == '\n') {*/
        /*new_indent = parse_indent();*/
        /*if (new_indent == -1) {*/
            /*[>ere;<]*/
            /*tok = NULL;*/
            /*return;*/
        /*}*/

        /*diff = new_indent - cur_indent;*/
        /*cur_indent = new_indent;*/
        /*debug_var("d", diff);*/

        /*parse_token();*/

        /*if (tok_len == 0)*/
            /*return;*/

        /*if (!strncmp("\\", tok, tok_len)) {*/
            /*if (diff == 1) {*/
                /*in += 1;*/
                /*chomp(' ');*/
                /*parse_token();*/
            /*} else {*/
                /*die("line continuation2");*/
            /*}*/
        /*} else {*/
            /*[>debug_var("d", diff);<]*/
            /*[>debug_var("d", new_indent);<]*/
            /*[>debug_var("d", *c);<]*/
            /*[>printf("tok '%.*s'\n", tok_len, tok);<]*/
            /*[>die("newline");<]*/
        /*}*/

        /*return;*/
    /*}*/

    /*parse_token();*/
    /*chomp(' ');*/
}


int
main(int argc, char **argv)
{
    if ((f = fopen(".\\src\\examples\\tokens0.ie", "r")) == NULL)
        die("failed to open file");

    read_line();

    depth = 0;
    state_fn[depth] = parse_prefix_head;

    while (state_fn[depth](), tok) {
        printf("tok: %d: '%.*s'\n", tok_len, tok_len, tok);
    }

    /*debug_var("d", depth);*/

    while (depth) {
        printf("%s\n", cmds[depth]);
        depth -= 1;
    }

    fclose(f);

    puts("bye");
    return 0;
}

