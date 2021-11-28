#include <stdio.h>
#include <string.h>
#include <stdlib.h>


struct dict_elem {
    char *name;
    int type;
    void *code;
    struct dict_elem *next ;
};

char memory[0xffff] = {0};
char *token = NULL;
FILE *f_input = NULL;
void *return_stack = &memory[0xfe00];
short *param_stack  = (short*)&memory[0xfd00];
char *tib          = &memory[0xfa00];
char *input        = &memory[0xf000];
char *input_head   = &memory[0xf000];
char *input_tail   = &memory[0xf000];
char *input_end    = &memory[0xfa00];
char *here         = &memory[0];
struct dict_elem *dict = NULL;
short *param_ptr = NULL;

void push_token(char *t);
void push_param(short s);
short pop_param(void);
void eval(const char * const token);
void die2(const char * const msg, const char * const file_name, const int line_number, const char * const func_name);
#define die(msg) die2(msg, __FILE__, __LINE__, __func__)
struct dict_elem* lookup(const char *name);
struct dict_elem* define(char *name, int type, void *code);
void* alloc(size_t size);
char * alloc_string(char *value);
char* next_token(void);

void parse_prefix(void);
void fn_add(void);
void fn_print_stack(void);


int
main(int argc, char **argv)
{
    puts("eval!");

    f_input = stdin;

    param_ptr = param_stack;

    define("[", 0, parse_prefix);
    define("+", 0, fn_add);
    define(".s", 0, fn_print_stack);

    while ((token = next_token()) != NULL)
        eval(token);
    
    fn_print_stack();

    puts("goodbye");

    return 0;
}


void
eval(const char * const token)
{
    long l = 0;
    char *endp = NULL;
    struct dict_elem *elem = NULL;
    void (*fn)(void) = NULL;

    /*printf("eval token: %s\n", token);*/

    if (*token == '\0')
        die("null char");

    if (*token == '"')
        die("double quote char");

    l = strtol(token, &endp, 10);
    if (endp == NULL) {
        die("endp is NULL");
    } else if (*endp == '\0') { 
        /*printf("long: %ld\n", l);*/
        push_param(l);
        return;
    } else {
        /*printf("not double: %s\n", token);*/
    }

    elem = lookup(token);
    if (elem == NULL)
        die("word not found");

    /*printf("dict elem: %s\n", elem->name);*/

    fn = elem->code;
    if (fn == NULL)
        die("missing function pointer");

    fn();
}


void
die2(const char * const msg, const char * const file_name, const int source_line_number, const char * const func_name)
{
    fprintf(stderr, "\nDIE: %s\n\n", msg);
    /*fprintf(stderr, "%3d: %s", line_number, buffer);*/
    /*fprintf(stderr, "     %*s^\n\n", i, "");*/
    fprintf(stderr, "%s : %d : %s\n\n", file_name, source_line_number, func_name);
    exit(1);
}


void
push_token(char *s)
{
    size_t len = strlen(s);
    char *new_tail = input_tail + len + 1;

    if (new_tail > input_end)
        die("overflow");

    strcpy(input_tail, s);

    input_tail = new_tail;
}


void
push_param(short s)
{
    *param_ptr = s;
    param_ptr += 1;
}


short
pop_param(void)
{
    param_ptr -= 1;
    return *param_ptr;
}


void
push_input(char *s)
{
    die(__func__);
}


void*
pop_input(void)
{
    die(__func__);
    return NULL;
}


struct dict_elem*
lookup(const char *name)
{
    struct dict_elem *elem = dict;
    /*printf("name: %s\n", name);*/

    while (elem) {
        /*printf("lookup elem: %p\n", elem);*/
        if (elem->name == NULL)
            die("missing name");

        /*printf("lookup elem->name: %s\n", elem->name);*/

        if (!strcmp(elem->name, name))
            return elem;

        elem = elem->next;
    }

    return NULL;
}


struct dict_elem*
define(char *name, int type, void *code)
{
    struct dict_elem *new = alloc(sizeof(struct dict_elem));
    char *new_name = alloc(strlen(name) + 1);

    strcpy(new_name, name);

    new->name = new_name;
    new->code = code;
    new->type = 0;
    new->next = dict;

    return dict = new;
}


void*
alloc(size_t size)
{
    void *rval = here;
    here += size;
    return rval;
}


void
parse_prefix(void)
{
    char cmd[1024];
    char *(expr_tokens[256]);
    char **expr_head = &expr_tokens[0];
    char **expr_tail = &expr_tokens[0];
    char **expr_end  = &expr_tokens[256];

    token = next_token();
    strcpy(cmd, token);
    token = next_token();

    while (token && strcmp(token, "]")) {
        if (!strcmp(token, "(")) {
            die("open paren");
        } else if (!strcmp(token, "{")) {
            die("open brace");
        } else if (!strcmp(token, "[")) {
            die("open bracket");
        } else {
            if (expr_tail == expr_end)
                die("overflow");

            *expr_tail = alloc_string(token);
            expr_tail += 1;
        }
        token = next_token();
    }

    if (token == NULL)
        die("eof");

    while (expr_head < expr_tail) {
        push_token(*expr_head);
        expr_head += 1;
    }

    push_token(cmd);

    return;
}


char *
next_token(void)
{
    char *new_line = NULL;

    if (input_head != input_tail) {
        size_t len = strlen(input_head);
        char *rval = input_head;
        input_head += len + 1;

        if (input_head == input_tail)
            input_head = input_tail = input;

        return rval;
    }

    if (fgets(tib, 1024, f_input) == NULL)
        return NULL;

    new_line = strrchr(tib, '\n');
    if (new_line)
        *new_line = '\0';

    return tib;
}


char *
alloc_string(char *value)
{
    char *new_string = alloc(strlen(value) + 1);
    strcpy(new_string, value);
    return new_string;
}


void
fn_add(void)
{
    short n2 = pop_param();
    short n1 = pop_param();
    short rval = n1 + n2;
    push_param(rval);
}


void
fn_print_stack(void)
{
    short *param_head = param_stack;
    printf("stack: ", *param_head);
    while (param_head < param_ptr) {
        printf("%d ", *param_head);
        param_head += 1;
    }
    printf("\n");
}

