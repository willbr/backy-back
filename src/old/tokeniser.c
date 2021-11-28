#include <stdlib.h> /* exit */
#include <stdio.h>
#include <string.h>

void read_line(void);
void tokenise_expr(void);
void tokenise_word(void);
void tokenise_prefix(void);
void parse_indent(void);
void die2(const char * const msg, const char * const file_name, const int line_number, const char * const func_name);
#define die(msg) die2(msg, __FILE__, __LINE__, __func__)
void chomp(char c);

#define false 0
#define true  -1

#define INDENT_WIDTH 2

int flag_echo_code = false;
FILE *f_input = NULL;

char buffer[1024] = "";
int i = 0;
int indent = 0;
int running = true;
int line_number = 0;

char *prefix_chars = "(){}[],\"\'&*";
char *break_chars = " (){}[],\n";


int
main(int argc, char **argv)
{
    for (argv += 1; *argv != NULL; argv += 1) {
        /*printf("arg: %s\n", *argv);*/
        if (!strcmp(*argv, "--echo-code")) {
            flag_echo_code = true;
        } else if (!strcmp(*argv, "-")) {
            f_input = stdin;
        } else {
            fprintf(stderr, "unknown arg: %s\n", *argv);
            exit(1);
        }
    }

    if (f_input == NULL)
        die("no input file");

    read_line();

    while (running) {
        tokenise_expr();
        /*read_line();*/
    }

    return 0;
}


void
read_line(void)
{
    line_number += 1;
    i = 0;

    if (fgets(buffer, sizeof(buffer), f_input) == NULL) {
        running = false;
        buffer[0] = '\0';
    }
}


void
chomp(char c) {
    while (buffer[i] != '\0' && buffer[i] == c)
        i += 1;
}

void
die2(const char * const msg, const char * const file_name, const int source_line_number, const char * const func_name)
{
    fprintf(stderr, "\nDIE: %s\n\n", msg);
    fprintf(stderr, "%3d: %s", line_number, buffer);
    fprintf(stderr, "     %*s^\n\n", i, "");
    fprintf(stderr, "%s : %d : %s\n\n", file_name, source_line_number, func_name);
    exit(1);
}


void
tokenise_expr(void)
{
    int start_indent = 0;

    if (buffer[i] == '\n')
        return;

    start_indent = indent;

    puts("[");

    while (buffer[i] != '\0') {
        /*printf("buffer[i]: '%c'\n", buffer[i]);*/
        if (buffer[i] == '\n') {
            parse_indent();
            /*fprintf(stderr, "indent: %d %d\n", start_indent, indent);*/
            if (indent > start_indent) {
                if (buffer[i] == '\0') {
                    break;
                } else if (buffer[i] == '\\') {
                    i += 1;
                    if (buffer[i] != ' ')
                        die("invalid char after line continuation");
                    i += 1;
                } else {
                    tokenise_expr();
                    if (indent == start_indent)
                        break;
                }
            } else if (indent == start_indent) {
                if (buffer[i] != '\\')
                    break;
                i += 1;
                if (buffer[i] != ' ')
                    die("invalid char");
            } else {
                break;
            }
        } else if (buffer[i] == ' ') {
            die("todo space");
        } else if (strchr(prefix_chars, buffer[i])) {
            tokenise_prefix();
        } else {
            tokenise_word();
        }
        chomp(' ');
    }
    puts("]");
}



void
parse_indent(void)
{
    int j = 0;

    while (running && buffer[i] != '\0' && buffer[i] == '\n') {
        read_line();
    }


    j = i;
    while (buffer[j] == ' ')
        j += 1;

    if (buffer[j] == '\n') {
        i = j + 1;
        return; /* skip empty line */
    }

    {
        int new_indent = 0;
        int delta = j - i;

        if (delta % INDENT_WIDTH != 0)
            die("bad indent1");

        new_indent = delta / INDENT_WIDTH;

        i = j;

        if (new_indent > indent + 1)
            die("bad indent2");

        indent = new_indent;
    }
}


void
tokenise_word(void)
{
    int j   = i;
    int len = 0;

    while (buffer[j] != '\0' && !strchr(break_chars, buffer[j]))
        j += 1;

    len = j - i;
    printf("%.*s\n", len, &buffer[i]);

    i = j;

    if (strchr("({[", buffer[j]))
        die("invalid char");
}


void
tokenise_prefix(void)
{
    int j = 0;
    int len = 0;

    switch (buffer[i]) {
    case '*':
        i += 1;
        if (strchr(break_chars, buffer[i])) {
            puts("*");
        } else if (strchr(prefix_chars, buffer[i])) {
            tokenise_prefix();
            die("todo prefix *");
        } else {
            die("todo prefix *");
        }
        break;

    case '(':
    case '{':
    case '[':
        printf("%c\n", buffer[i]);
        i += 1;
        break;

    case ')':
    case '}':
    case ']':
        printf("%c\n", buffer[i]);
        i += 1;
        if (!strchr(" \n(){}[],", buffer[i]))
            die("invalid char following close");
        break;

    case ',':
        printf("%c\n", buffer[i]);
        i += 1;
        if (!strchr(" \n(){}[]", buffer[i]))
            die("invalid char following close");
        break;

    case '"':
        j = i + 1;

        while (buffer[j] != '\0') {
            if (buffer[j] == '"') {
                j += 1;
                break;
            } else if (buffer[j] == '\\') {
                die("escape");
            }
            j += 1;
        }

        len = j - i;
        printf("%.*s\n", len, &buffer[i]);
        i = j;
        break;

    default:
        die("todo unknown prefix char");
    }
}

