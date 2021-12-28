from multiprocessing import Pool
from subprocess import Popen, run, PIPE
from difflib import context_diff, unified_diff, ndiff
from helper import *


def run_test(t):
    basename, prog, er = t

    # print(repr(prog))
    p = Popen(["tcc", "-run", "./src/c/parse.c", "-"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = [x.decode() for x in p.communicate(prog.encode())]

    if err:
        return err

    er  = er.split('\n')
    out = out.replace('\r\n', '\n').strip().split('\n')

    # print(er)
    # print(out)

    diff = '\n'.join(unified_diff(out, er))
    if diff != '':
        print("File:")
        print(basename)
        print("Expected:")
        print('\n'.join(er))
        print("\nOutput:")
        print(' '.join(out))
        print()
        return diff

    return None


if __name__ == '__main__':
    number_of_tests = 0
    fails = 0

    with Pool(1) as p:
        for r in p.map(run_test, tests()):
            number_of_tests += 1
            # print(r)
            if r:
                fails += 1
                print(r)
            pass

    if fails:
        print(f"{fails=}")
        print(f"{number_of_tests=}")
    else:
        print("all passed")
        print(f"{number_of_tests=}")

