#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int
main(int argc, char **argv)
{
    char token[256] = "";
    char *code = "1 2 +\n3 + ";
    char *s = code;

    while (*s != '\0') {
        int   len = 0;
        char *end = NULL;

        while (*s == ' ' || *s == '\n')
            s += 1;

        end = s;

        while (*end != ' ' && *end != '\n' && *end != '\0')
            end += 1;

        len = end - s;
        /*printf("len: %d\n", len);*/

        if (len == 0)
            break;

        strncpy(token, s, len);

        printf("t: %s\n", token);

        s = end;
    }

    return 0;
}

