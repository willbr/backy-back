# reader
    read first char
    is it a prefix char? "({[*&'
        " string
        ( infix
        { rpn
        [ prefix
        * deref
        & address
        ' quote
        % binary
        $ hexadecimal

    read word
    try and promote to number

# assignment syntax
special case for infix assignment

    a = 5

to

    5 a !

instead of

    a 5 =

# implied infix

    1 + 1
    is
    (1 + 1)

    to

    1 1 +


or

    a = 10

    to

    10 a !

# prefix chars

pointer methods

    * deref
    & addr
    ' quote
    ! not

# neoteric function calls

    printf("hello %s", "Bob")

    to

    [printf ("hello %s", "Bob")]

do I need to swap the argument orders?
is this only needed for vaargs?

look into how Forth does printf
look into how Lisp does printf

    printf("hello %s!\n", name)

    to

    printf "hello %s!\n" name

    to

    name "hello %s!\n" printf


or cound the number of arguments?

    printf("hello %s!\n", name)

    to

    printf "hello %s!\n" name 2


# struct access

    struct ball
      x float
      y float

    var my-ball = ball(0, 0)

    puts my-ball.x

# keep assignment and equality explicit

    set a 10

    set set
    :=  let
     =  equals or ==


# add forth memory model

    mem = bytearray(0x8000)

# have modes: 8bit, 16bit, 32bit, 64bit

Review how Uxa does this

stack functions

    push
    pop
    peek
    print
    get

# typed version

object is a union, it can be a list or a void*

    struct list {
        struct object *elem;
        struct object *next;
    }

    struct object {
        int tag;
        union {
            void *vs;
        } u;
    }

# include version numbers

    version 0

