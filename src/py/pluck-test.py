from sys import argv, exit
from helper import *

def main():
    try:
        i = int(argv[1])
    except ValueError as e:
        print(e)
        exit(1)

    basename, prog, er = tests()[i]
    print(prog)


if __name__ == '__main__':
    main()
