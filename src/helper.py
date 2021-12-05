from os import path

script_dir = path.dirname(path.realpath(__file__))

def parse_output(o):
    return '\n'.join([x.strip() for x in o.split('\n')])


def parse_test(t):
    arg, er = [x.strip() for x in t.split("-----")]
    return arg, parse_output(er)


def tests():
    test_path = path.join(script_dir, "tests.txt")
    with open(test_path) as f:
        return [parse_test(t) for t in f.read().split("#####")]

