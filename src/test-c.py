from multiprocessing import Pool
from subprocess import run, PIPE


def parse_output(o):
    return [x.strip() for x in o.split('\n')]


def parse_test(t):
    arg, er = [x.strip() for x in t.split("-----")]
    return arg, parse_output(er)


def tests():
    with open("./src/tests.txt") as f:
        return [parse_test(t) for t in f.read().split("#####")]


def f(x):
    print(x)
    cp = None
    # cp = run(["tcc", "-run", "./src/parse.c", "-"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # cp.communicate("hello")
    # print(cp)
    return cp


if __name__ == '__main__':
    with Pool(1) as p:
        for r in p.map(f, tests()):
            # print(r.stdout)
            pass

	# tcc -run src/parse.c

