# backy-back

stack lang

a little bit of forth, python & lisp

## implied infix

    1 + 1
    is
    (1 + 1)

    to

    1 1 +


or

    a = 10

    to

    10 a !

## assignment syntax
special case for infix assignment

    a = 5

to

    5 a !

instead of

    a 5 =

## struct access

    struct ball
      x float
      y float

    var my-ball = ball(0, 0)

    puts my-ball.x

## keep assignment and equality explicit

    set a 10

    set set
    :=  let
     =  equals or ==

## add forth memory model

    mem = bytearray(0x8000)

## have modes: 8bit, 16bit, 32bit, 64bit

Review how Uxa does this

stack functions

    push
    pop
    peek
    print
    get

## typed version

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

## include version numbers

    version 0

## heredocs

    puts <<end
    hello,
    How are you doing today?
    bye!
    end

## regex

create a regex object

    /^haha$/

## add rpn command 

so I can write reverse polish notation as a statement

    emit 42

    rpn 42 emit

