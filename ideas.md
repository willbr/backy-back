# reader
    read first char
    is it a breakchar char? " \t\n,;()[]{}'
          space
       \t tab is an error
       \n newline
        , comma
        ; semicolon
        ( infix
        { rpn
        [ prefix

    is it a prefix char?
        " string
        * deref
        & address
        ' quote
        % binary
        $ hexadecimal

    read word
    try promote functions
        - promote to number
        - promote to number from hex
        - promote to number from binary


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

# add promotion stage
apply a list of transformations to a token

    *something

becomes:

    deref something
    [deref something]
    deref(something)

# neoteric function calls

    printf("hello %s", "Bob")

    to

    [printf ("hello %s", "Bob")]

    tokens:
    [ printf ( "hello %s" , "Bob" ) ]

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

object is a union, it can be a list or a void\*

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

# heredocs
    puts <<end
    hello,
    How are you doing today?
    bye!
    end

# regex
create a regex object

    /^haha$/

# add rpn command 
so I can write reverse polish notation as a statement

    emit 42

    rpn 42 emit

# toco

## add an escape for c code

    raw-c "#define SDL_MAIN_HANDLED"
    raw-c "int a = 0;"


## add println & fprintln macros

    a := float(3.6)

    println "float: {a:4.2f}"
    fprintln stderr "{a=}

to

    float a = 3.6;

    printf("float: %3.6f\n")
    fprintf(stderr, "a=%f", a);


