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
        print("#Error:")
        print(f"{basename=}")
        print("prog")
        print(prog.replace(' ', '.'))
        print("out")
        print(out)
        print("err", err)
        return err

    er  = er.strip().split('\n')
    out = out.replace('\r\n', '\n').strip().split('\n')

    #print(er)
    #print(out)

    diff = '\n'.join(unified_diff(out, er))
    if diff != '':
        err_msg = '\n'.join([
            "\nFile:",
            basename,
            "\nInput:",
            prog,
            "\nExpected:",
            ' '.join(er),
            "\nOutput:",
            ' '.join(out),
            "\nDiff:",
            diff,
            ])
        return err_msg
    else:
        # print("good: ", basename)
        pass

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

    print(f"{fails=}" if fails else "all passed")
    print(f"{number_of_tests=}")

